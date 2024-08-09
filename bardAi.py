import time

from bardapi import Bard
import requests
from cachetools import TTLCache
from commonUtils.log import logger
from DrissionPage import ChromiumPage, ChromiumOptions
import yaml

from sendEmail import sendEmail



class bardAi:
    # 创建一个最多包含3个元素的自动过期的哈希映射，每个元素的生存时间为24小时
    cache = TTLCache(maxsize=30, ttl=60 * 60 * 24)

    PSID = None
    PSIDCC = None
    PSIDTS = None


    username = None
    password = None
    imagePath = None

    @staticmethod
    def getAnswer(content: str, conversationId: str, imageFileName: str):
        # logger.info('询问的内容：{}'.format(content))
        bard = bardAi.cache.get(conversationId)
        # logger.info('获取的bard：{}'.format(bard))
        if bard is None:
            logger.info('获取的bard，新的conversationId：{}'.format(conversationId))
            bard = bardAi.getBard()
        bardAi.cache[conversationId] = bard

        if imageFileName:
            image_path = bardAi.imagePath + imageFileName
            logger.info('读取图片路径：{}'.format(image_path))
            image = open(image_path, 'rb').read()  # (jpeg, png, webp) are supported.
            res = bard.ask_about_image(content, image)
        else:
            res = bard.get_answer(content)

        resContent = res['content']
        imageLinks = []
        # imageImages = []
        try:
            imageLinks = res['links']
            # imageImages = res['images']
        except Exception as e:
            logger.error('获取links报错：%s', e)
        logger.info('获取的imageLinks：{}'.format(imageLinks))
        # logger.info('获取的imageImages：{}'.format(imageImages))

        if imageLinks and len(imageLinks) > 0:
            #logger.info('获取的resContent：{}'.format(resContent))
            #logger.info('获取的imageLinks：{}'.format(imageLinks))
            return resContent, imageLinks
        return resContent, None

    @staticmethod
    def getBard():
        if bardAi.PSID is None:
            if bardAi.username is None:
                with open('config/config.yml', 'r', encoding='utf-8') as f:
                    configs = yaml.load(f, Loader=yaml.FullLoader)
                bardAi.username = configs['bardAi']['username']
                bardAi.password = configs['bardAi']['password']
                bardAi.imagePath = configs['bardAi']['image_path']
            bardAi.updatePSID(bardAi.username, bardAi.password)

        session = requests.Session()
        session.headers = {
            "Host": "gemini.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://gemini.google.com",
            "Referer": "https://gemini.google.com/",
        }
        session.cookies.set("__Secure-1PSID", bardAi.PSID)
        session.cookies.set("__Secure-1PSIDCC", bardAi.PSIDCC)
        session.cookies.set("__Secure-1PSIDTS", bardAi.PSIDTS)

        # Give session and conversation id. (check manually)
        return Bard(token=bardAi.PSID, session=session, timeout=30)


    @staticmethod
    def updatePSID(username: str, password: str):
        global page
        # logger.info('获取PSID：{}'.format(username))
        if not username:
            raise Exception('invalid username.')
        if not password:
            raise Exception('invalid password.')
        try:


            # co = ChromiumOptions().set_paths(local_port=9111, browser_path=r'/opt/microsoft/msedge-dev/microsoft-edge', user_data_path=r'/tmp/DrissionPage/userData_9111')
            # co = ChromiumOptions().set_paths(local_port=9222)
            co = ChromiumOptions().set_paths( browser_path=r'/opt/google/chrome/google-chrome', user_data_path=r'/tmp/DrissionPage/userData_9211')
            co.set_argument('--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            co.set_argument('--headless')
            # co.set_argument('--incognito')
            # co.set_argument('--no-sandbox')
            co.set_timeouts(implicit=20)
            # 创建页面对象，并启动或接管浏览器
            page = ChromiumPage(addr_driver_opts=co)

            # page.screencast.set_mode.video_mode()
            # page.screencast.set_save_path('video')  # 设置视频存放路径
            # page.screencast.start()


            page.get('https://gemini.google.com/')
            logger.info('打开页面了')

            recaptcha = page.ele('#recaptcha', timeout=2)
            if recaptcha:
                logger.info('出现了验证')
                iframe = page.ele('tag:iframe@src^https://www.google.com/recaptcha')
                logger.info('找到了iframe')
                iframe = page.get_frame(iframe)
                anchor = iframe.ele('#recaptcha-anchor')
                checkmark = anchor.ele('tag:div@class=recaptcha-checkbox-checkmark')
                logger.info('找到了验证按钮')
                time.sleep(3)
                for i in range(10):
                    checkmark.click()
                logger.info('点击了验证按钮')

            # 是否有弹出框
            loginBtn = page.ele('#gb').ele('tag:span@|text()=登录@|text()=Sign in', timeout=2)
            if loginBtn:
                logger.info('有登录按钮，先登录')
                loginBtn.click(by_js=True)

                againBtn = page.ele('tag:div@class=Z6Ep7d', timeout=2)
                if againBtn:
                    logger.info('有try again按钮，先点击')
                    againBtn.click(by_js=True)
                    againBtn.click()

                email = page.ele('#identifierId')
                email.input(username)
                nextBtn = page.ele('#identifierNext')
                nextBtn.click()
                logger.info('填写了账号，点击了下一步按钮')

                passwordInput = page.ele('#password').ele('tag:input@type=password')
                passwordInput.wait.display()
                passwordInput.input(password)
                passwordNext = page.ele('#passwordNext')
                passwordNext.click(by_js=True)
                logger.info('点击了密码的下一步按钮')

            page.ele('tag:img@class=gb_n gbii')
            logger.info('出现登录后的头像')

            # textarea = page.ele('tag:rich-textarea')
            # textarea.input('你好')
            # send = page.ele('tag:div@class:send-button-container').ele('tag:button@mat-ripple-loader-class-name=mat-mdc-button-ripple')
            # send.click(by_js=True)
            # time.sleep(3)

            # page.get_screenshot('updatePSID-info.png')
            for cookie in page.get_cookies():
                #logger.info('成功获取cookie：{}'.format(cookie))
                if cookie['name'] == '__Secure-1PSID':
                    bardAi.PSID = cookie['value']
                    # if cookie['value'].endswith('.'):
                    #     bardAi.PSID = cookie['value']
                if cookie['name'] == '__Secure-1PSIDCC':
                    bardAi.PSIDCC = cookie['value']
                if cookie['name'] == '__Secure-1PSIDTS':
                    bardAi.PSIDTS = cookie['value']
            logger.info('成功获取PSID：{}'.format(bardAi.PSID))
            logger.info('成功获取PSIDCC：{}'.format(bardAi.PSIDCC))
            logger.info('成功获取PSIDTS：{}'.format(bardAi.PSIDTS))
            if bardAi.PSID is None:
                # logger.info('打印html信息：%s', page.html)
                logger.error('bardAI-获取PSID失败')
                image_data = page.get_screenshot(as_base64='jpg')
                sendEmail.send('bardAI-获取PSID失败失败', image_data)
                return
        except Exception as e:
            # logger.error('打印html信息：%s', page.html)
            logger.error('updatePSID报错：%s', e)
            image_data = page.get_screenshot(as_base64='jpg')
            sendEmail.send(f'用户名：{username},获取bard的token报错：{e}', image_data)
        finally:
            # page.screencast.stop()
            page.quit()


