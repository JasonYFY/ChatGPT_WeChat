import random
import sys
import platform
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyppeteer import launch
from urllib.request import urlretrieve
from PIL import Image
import cv2
import os
from commonUtils.log import logger
app = FastAPI()



class LoginRequest(BaseModel):
    username: str
    password: str


def printf(message):
    print(message)
    sys.stdout.flush()


async def get_jd_ck(usernum, passwd, headless=True):
    async def typeuser(page, usernum, passwd):
        logger.info("输入用户名和密码")
        zmBtn = '.J_ping.planBLogin'
        element = await page.querySelector(zmBtn)
        # 如果元素存在，则点击
        if element:
            await click_and_wait(page, zmBtn)
        await wait_and_type(page, '#username', usernum, (60, 121))
        await wait_and_type(page, '#pwd', passwd, (100, 151))
        await page.waitFor(random.randint(100, 2000))

        fxkBtm = '.policy_tip-checkbox'
        checkbox = await page.querySelector(fxkBtm)
        # 检查复选框是否被选中
        is_checked = await page.evaluate(
            '(element) => element.checked', checkbox
        )
        # 如果未选中，则点击
        if not is_checked:
            await checkbox.click()
            await page.waitFor(random.randint(1000, 2000))
        # 检查复选框是否被选中
        is_checked = await page.evaluate(
            '(element) => element.checked', checkbox
        )
        logger.info(f"复选框是否被选中: {is_checked}")
        # await click_and_wait(page, fxkBtm)
        await click_and_wait(page, '.btn.J_ping.btn-active')
        logger.info("完成用户名和密码输入")

    async def verification(page):
        logger.info("开始滑块验证")
        await page.waitForSelector('#cpc_img')
        image_src = await page.Jeval('#cpc_img', 'el => el.getAttribute("src")')
        urlretrieve(image_src, 'image.png')
        width = await page.evaluate('() => { return document.getElementById("cpc_img").clientWidth; }')
        height = await page.evaluate('() => { return document.getElementById("cpc_img").clientHeight; }')
        image = Image.open('image.png')
        resized_image = image.resize((width, height))
        resized_image.save('image.png')
        template_src = await page.Jeval('#small_img', 'el => el.getAttribute("src")')
        urlretrieve(template_src, 'template.png')
        width = await page.evaluate('() => { return document.getElementById("small_img").clientWidth; }')
        height = await page.evaluate('() => { return document.getElementById("small_img").clientHeight; }')
        image = Image.open('template.png')
        resized_image = image.resize((width, height))
        resized_image.save('template.png')
        await page.waitFor(100)
        el = await page.querySelector("#captcha_modal > div > div.captcha_footer > div > img")
        box = await el.boundingBox()
        distance = await get_distance()
        await page.mouse.move(box['x'] + 10, box['y'] + 10)
        await page.mouse.down()
        await page.mouse.move(box['x'] + distance + random.uniform(8, 25), box['y'], {'steps': 10})
        await page.waitFor(random.randint(100, 500))
        await page.mouse.move(box['x'] + distance, box['y'], {'steps': 10})
        await page.mouse.up()
        await page.waitFor(3000)
        cleanup_files('image.png', 'template.png')
        logger.info("完成滑块验证")

    async def get_distance():
        img = cv2.imread('image.png', 0)
        template = cv2.imread('template.png', 0)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        template = cv2.GaussianBlur(template, (5, 5), 0)
        bg_edge = cv2.Canny(img, 100, 200)
        cut_edge = cv2.Canny(template, 100, 200)
        img = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        template = cv2.cvtColor(cut_edge, cv2.COLOR_GRAY2RGB)
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        value = cv2.minMaxLoc(res)[3][0]
        distance = value + 10
        return distance

    async def validate_logon(usernum, passwd):
        browser_path = await init_chrome()
        if not browser_path:
            raise Exception("未能找到或下载Chrome浏览器")

        if not os.path.isfile(browser_path):
            logger.error(f"Chromium 文件不存在：{browser_path}")
            raise Exception(f"Chromium 文件不存在：{browser_path}")

        browser = await launch({
            'executablePath': browser_path,
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--proxy-bypass-list=*',
                '--disable-extensions',
                '--start-maximized'
            ],
            'ignoreDefaultArgs': ['--enable-automation']
        })
        logger.info("Browser launched successfully")
        page = await browser.newPage()
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        await page.setViewport({'width': 1366, 'height': 768})
        try:
            await asyncio.wait_for(page.goto(
                'https://plogin.m.jd.com/login/login?appid=300&returnurl=https%3A%2F%2Fm.jd.com%2F&source=wq_passport',
                {'waitUntil': 'networkidle2', 'timeout': 60000}), timeout=60)
        except asyncio.TimeoutError:
            return await handle_error(f"{usernum} 加载页面超时", browser)
        except Exception as e:
            return await handle_error(f"{usernum} 访问页面出错", browser, e)

        await typeuser(page, usernum, passwd)

        retries = 0
        max_retries = 10  # 设置最大重试次数
        while retries < max_retries:
            retries += 1
            logger.info(f"重试次数：{retries}")
            try:
                error_elements = await page.xpath(
                    "//*[contains(text(), '账号或密码不正确') or contains(text(), '密码错误')]")
                if error_elements:
                    return await handle_error(f"{usernum} 账号或密码不正确，跳过登录", browser)
            except Exception as e:
                return await handle_error(f"{usernum} 检查账号或密码错误时出错", browser, e)

            try:
                dialog_elements = await page.J('.dialog-des')
                if dialog_elements:
                    dialog_text = await page.evaluate('(element) => element.textContent', dialog_elements)
                    if '您的账号存在风险' in dialog_text or '实名认证' in dialog_text:
                        return await handle_error(f"{usernum} 需要进行实名认证，跳过登录", browser)
            except Exception as e:
                return await handle_error(f"{usernum} 处理实名认证对话框时发生错误", browser, e)

            try:
                if await page.J('#searchWrapper'):
                    cookies = await page.cookies()
                    pt_key = ''
                    pt_pin = ''
                    for cookie in cookies:
                        if cookie['name'] == 'pt_key':
                            pt_key = cookie['value']
                        elif cookie['name'] == 'pt_pin':
                            pt_pin = cookie['value']
                    await browser.close()
                    printf(f"{usernum} 登录成功，获取到CK: pt_key={pt_key};pt_pin={pt_pin};")
                    return {"status": "true", "data": f'pt_key={pt_key};pt_pin={pt_pin};'}
            except Exception as e:
                return await handle_error(f"{usernum} 登录发生错误", browser, e)

            try:
                if await page.J('.sub-title'):
                    return await handle_error(f"{usernum} 需要进行短信验证", browser)
            except Exception as e:
                return await handle_error(f"{usernum} 短信验证发生错误", browser, e)
            # page.waitFor(3000)
            try:
                if await page.waitForXPath('//*[@id="small_img"]', {'timeout': 2000}):
                    await verification(page)
            except Exception as e:
                return await handle_error(f"{usernum} 滑块验证发生错误", browser, e)

            try:
                if await page.xpath('//*[@id="captcha_modal"]/div/div[3]/button'):
                    await page.waitFor(3000)
                    printf("点击滑块验证过不了，刷新重试……")
                    await page.reload()
                    await typeuser(page, usernum, passwd)
            except Exception as e:
                return await handle_error(f"{usernum} 重试登录滑块发生错误", browser, e)

        return await handle_error(f"{usernum} 超过最大重试次数，登录失败", browser)

    return await asyncio.wait_for(validate_logon(usernum, passwd), timeout=300)


async def init_chrome():
    if platform.system() == 'Windows':
        chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_exe):
            return chrome_exe
        else:
            raise Exception(f"未找到Chrome浏览器，请确认路径是否正确：{chrome_exe}")

    elif platform.system() == 'Linux':
        chrome_path = os.path.expanduser("/home/yifangyujason/.local/share/pyppeteer/local-chromium/1181205/chrome-linux/chrome")
        if os.path.isfile(chrome_path):
            return chrome_path
        else:
            logger.error(f"Chromium 路径不存在：{chrome_path}")
            return None

    elif platform.system() == 'Darwin':
        return 'mac'
    else:
        return 'unknown'


async def handle_error(error_message, browser, e=None):
    if e:
        logger.error(f"{error_message}: {e}", exc_info=True)
    else:
        logger.error(error_message)
    if browser:
        await browser.close()
    return {"status": "fail", "msg": error_message}


async def click_and_wait(page, selector, wait_time=2000):
    await page.click(selector)
    await page.waitFor(random.randint(100, wait_time))


async def wait_and_type(page, selector, text, delay_range):
    await page.waitForSelector(selector)
    await page.type(selector, text, {'delay': random.randint(*delay_range)})


def cleanup_files(*filenames):
    for filename in filenames:
        if os.path.exists(filename):
            os.remove(filename)


@app.post("/getJingdongToken")
async def login(request: LoginRequest):
    try:
        response = await get_jd_ck(request.username, request.password, headless=False)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{request.username}账密登录发生异常:{e}")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
