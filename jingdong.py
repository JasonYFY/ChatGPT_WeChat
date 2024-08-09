# -*- coding: utf-8 -*-

import time

from DrissionPage import ChromiumPage, ChromiumOptions

from commonUtils.log import logger
from jigsawCaptcha import detect_displacement
from ocrPng import recognize_text_Paddle
from sendEmail import sendEmail
import numpy as np
import cv2
# from matplotlib import pyplot as plt
from PIL import Image
from io import BytesIO
from DrissionPage.common import ActionChains


class jingdong:

    @staticmethod
    def getToken(username: str, password: str):
        global page
        logger.info('用户名：{}'.format(username))
        if not username:
            raise Exception('invalid username.')
        if not password:
            raise Exception('invalid password.')
        try:

            # co = ChromiumOptions().set_paths(local_port=9222)
            co = ChromiumOptions().set_paths(local_port=9211, browser_path=r'/opt/google/chrome/google-chrome',
                                             user_data_path=r'/tmp/DrissionPage/userData_9211')
            co.set_argument('--user-agent',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

            # 设置用隐身模式启动浏览器
            co.set_argument('--incognito')
            co.set_argument('--no-sandbox')
            co.set_argument('--headless')
            co.set_timeouts(implicit=20)
            # 创建页面对象，并启动或接管浏览器
            page = ChromiumPage(addr_driver_opts=co)
            page.get('https://m.jd.com/')
            logger.info('打开页面了')

            # 点击登录头像
            loginBtn = page.ele('#mCommonMy')
            loginBtn.click(by_js=True)

            pt_key = None
            pt_pin = None
            # 点击账号密码登录按钮
            time.sleep(1)
            zmBtn = page.ele('tag:span@report-eventid=MLoginRegister_SMSVerification')
            zmBtn.wait.display()
            zmBtn.wait.not_covered()

            zmBtn.click(by_js=True)
            logger.info('点击了账号密码登录')

            # 填写账号密码
            usernameInput = page.ele('#username')
            usernameInput.wait.display()
            usernameInput.input(username)
            passwordInput = page.ele('#pwd')
            passwordInput.input(password)
            gxBtn = page.ele('tag:input@class=policy_tip-checkbox')
            gxBtn.click(by_js=True)
            # gxBtn.click()
            time.sleep(1)
            if not gxBtn.states.is_checked:
                logger.info('勾选失败，继续勾选')
                gxBtn.click(by_js=True)
            time.sleep(1)
            login = page.ele('tag:a@report-eventid=MLoginRegister_Login')
            login.wait.enabled()
            login.click(by_js=True)
            logger.info('点击了登录按钮')
            time.sleep(2)
            captcha_modal = page.ele('#captcha_modal')

            # 获取验证码图片
            cpc_img = page.ele('#cpc_img').get_src()
            small_img = page.ele('#small_img').get_src()

            top_left = detect_displacement(small_img, cpc_img)
            logger.info('计算出拖拽的距离：{}'.format(top_left))

            # 拖拽
            imgBtn = captcha_modal.ele('tag:div@class:sp_msg').ele('tag:img')
            # logger.info(imgBtn)

            imgBtn.drag(top_left + 7, 0, 1.5)

            logger.info('拖拽完成')
            time.sleep(1)
            tip = page.ele('tag:div@class=tip', timeout=2)
            # 记录上一次的提示词
            lastTipText = None
            if tip:
                ac = ActionChains(page)
                logger.info('有颜色验证码出现')
                for i in range(20):

                    # 识别图片中的文字
                    tipPic = tip.ele('tag:img')
                    # tipPic.get_screenshot('tipPic.png')
                    # tipPic.get_screenshot(as_bytes='png')
                    # tipPic.get_src()
                    text = recognize_text_Paddle(tipPic.get_screenshot(as_bytes='png'))
                    logger.info('提示词：{}'.format(text))
                    if not text:
                        logger.info('提示词为空,可能成功了，等待多几秒，然后获取token')
                        time.sleep(3)
                        # 获取cookie
                        pt_key, pt_pin = jingdong.getCookie(page, pt_key, pt_pin)
                        break
                    if lastTipText and lastTipText == text:
                        logger.info('与上一次的提示词相同，可能成功了，等待几秒，然后获取token')
                        time.sleep(3)
                        # 获取cookie
                        pt_key, pt_pin = jingdong.getCookie(page, pt_key, pt_pin)
                        # 不为空时才退出循环，免得误判
                        if pt_key is not None:
                            break

                    lastTipText = text

                    cpcImg = page.ele('#cpc_img')
                    cpc_img = cpcImg.get_src()
                    width, height = cpcImg.size
                    # 将字节数据转换为NumPy数组
                    img0 = Image.open(BytesIO(cpc_img)).convert("RGB")
                    img0 = np.array(img0)
                    img0 = cv2.resize(img0, (width, height), interpolation=cv2.INTER_LINEAR)
                    # img0 = cv2.resize(img0, (420, 276), interpolation=cv2.INTER_LINEAR)
                    # plt.imshow(img0)
                    # plt.show()
                    ar = img0.copy()

                    # 判断字符串中是否包含 "绿色"
                    if "绿色" in text:
                        logger.info('提示词包含绿色')
                        # 找到绿色
                        ar[(ar[:, :, 0] < 100) & (ar[:, :, 1] > 150) & (ar[:, :, 2] < 100)] = [255, 0, 0]
                        # 找到第一个值为[255, 0, 0]的点
                    elif "蓝色" in text:
                        logger.info('提示词包含蓝色')
                        # 找到蓝色
                        ar[(ar[:, :, 0] < 100) & (ar[:, :, 1] < 150) & (ar[:, :, 2] > 200)] = [255, 0, 0]
                    elif "紫色" in text:
                        logger.info('提示词包含紫色')
                        # 找到紫色
                        ar[(ar[:, :, 0] > 100) & (ar[:, :, 1] < 50) & (ar[:, :, 2] > 100)] = [255, 0, 0]
                    elif "红色" in text:
                        logger.info('提示词包含红色')
                        # 红色
                        ar[(ar[:, :, 0] > 200) & (ar[:, :, 1] < 100) & (ar[:, :, 2] < 50)] = [255, 0, 0]
                    else:
                        # 找到黄色 淡黄色 黄色是 [255, 255, 0]
                        ar[(ar[:, :, 0] > 200) & (ar[:, :, 1] > 200) & (ar[:, :, 2] < 100)] = [255, 0, 0]
                        # 找到第一个值为[255, 0, 0]的点 这个是红色的RGB
                        # x, y = np.where((ar[:, :, 0] == 255) & (ar[:, :, 1] == 0) & (ar[:, :, 2] == 0))
                    x, y = np.where((ar[:, :, 0] == 255) & (ar[:, :, 1] == 0) & (ar[:, :, 2] == 0))
                    if len(x) == 0:
                        cpc_img = page.ele('#cpc_img')
                        time.sleep(1)
                        ac.move_to(cpc_img).click()
                        time.sleep(1)
                        submmit = page.ele('tag:button@class=sure_btn')
                        submmit.click(by_js=True)
                        # time.sleep(1)
                        # continue
                    else:
                        # 取出中间的一个点
                        x = x[len(x) // 2]
                        y = y[len(y) // 2]
                        # y是从左边开始数的点
                        x = int(x)
                        y = int(y)
                        # print(x, y)
                        # 点击
                        try:
                            cpc_img = page.ele('#cpc_img')
                            # ac.move_to(cpc_img, 0, 0).click()
                            # ac.move_to(cpc_img, -50, -50).click() # 这个是圈外？
                            # ac.move_to(cpc_img, 50, 50).click() # 这个是左上角
                            # ac.move_to(cpc_img, 25, 25).click() # 这个是更加左上角
                            # ac.move_to(cpc_img, 50, 0).click() #上面的x轴
                            # ac.move_to(cpc_img, 0, 50).click() #y轴
                            # ac.move_to(cpc_img, 0, height-20).click()
                            time.sleep(1)
                            ac.move_to(cpc_img, y, x).click()
                            time.sleep(1)
                            submmit = page.ele('tag:button@class=sure_btn')
                            submmit.click(by_js=True)
                        # print(cookies)
                        # if cookies.index("pt_token") != -1:
                        #     return cookies
                        except Exception as e:
                            logger.error('京东getToken-解决颜色验证码报错：%s', e)
                            pass
                    time.sleep(2)
                    captcha_modal = page.ele('#captcha_modal', timeout=3)
                    if not captcha_modal:
                        logger.info('安全验证框消失了,可能成功了，等待多几秒，然后获取token')
                        time.sleep(3)
                    loading = page.is_loading
                    if loading:
                        logger.info('目前处于加载状态，再等待几秒')
                        time.sleep(2)
                    # 获取cookie
                    pt_key, pt_pin = jingdong.getCookie(page, pt_key, pt_pin)
                    if pt_key is not None:
                        logger.info('京东getToken-获取到pt_key：%s', pt_key)
                        logger.info('京东getToken-获取到pt_pin：%s', pt_pin)
                        break
                    # time.sleep(2)
                    logger.info('没成功，重新识别：{}'.format(i))
            else:
                logger.info('颜色验证码没有出现')
                captcha_modal = page.ele('#captcha_modal', timeout=5)
                if not captcha_modal:
                    logger.info('安全验证框消失了,可能成功了，等待多几秒，然后获取token')
                    time.sleep(3)
                # 获取cookie
                pt_key, pt_pin = jingdong.getCookie(page, pt_key, pt_pin)
            if pt_key is None:
                logger.error('京东getToken-获取不到')
                image_data = page.get_screenshot(as_base64='jpg')
                sendEmail.send(f'用户名：{username},获取京东token失败', image_data)
                return
            return pt_key, pt_pin

        except Exception as e:
            logger.error('京东getToken报错：%s', e)
            image_data = page.get_screenshot(as_base64='jpg')
            sendEmail.send(f'用户名：{username},获取京东token报错：{e}', image_data)
            raise
        finally:
            # page.screencast.stop()
            page.quit()

    @staticmethod
    def getCookie(page, pt_key, pt_pin):
        # 获取cookie
        for cookie in page.get_cookies():
            if cookie['name'] == 'pt_key':
                pt_key = cookie['name'] + '=' + cookie['value']
            if cookie['name'] == 'pt_pin':
                pt_pin = cookie['name'] + '=' + cookie['value']
        return pt_key, pt_pin
