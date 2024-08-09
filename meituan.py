# -*- coding: utf-8 -*-

import time

from DrissionPage import ChromiumPage, ChromiumOptions

from ReceiveEmail import EmailClient
from commonUtils.log import logger
from sendEmail import sendEmail


class meituan:

    @staticmethod
    def getToken(username: str, password: str):
        global page
        logger.info('用户名：{}'.format(username))
        if not username:
            raise Exception('invalid username.')
        if not password:
            raise Exception('invalid password.')
        try:
            #co = ChromiumOptions().use_system_user_path()
            # / opt / google / chrome / google - chrome
            # co = ChromiumOptions().set_paths(local_port=9222)
            co = ChromiumOptions().set_paths(local_port=9222, browser_path=r'/opt/google/chrome/google-chrome', user_data_path=r'/tmp/DrissionPage/userData_9222')

            # 设置用隐身模式启动浏览器
            # co.set_argument('--incognito')
            # co.set_argument('--no-sandbox')
            # co.set_argument('--disable-plugins-discovery')
            co.set_argument('--headless')
            co.set_timeouts(implicit=20)
            # 创建页面对象，并启动或接管浏览器
            page = ChromiumPage(co)
            page.get('https://i.meituan.com/s/')
            logger.info('打开页面了')

            # 获取cookie
            for cookie in page.get_cookies():
                if cookie['name'] == 'token':
                    token = cookie['value']
                    logger.info(token)
                    return token

            phoneNumInput = page.ele('#phoneNumInput', timeout=2)
            if phoneNumInput:
                logger.info('未登录')
                phoneNumInput.input(username)

                sendCodeBtn = page.ele('#sendCodeBtn')
                logger.info(sendCodeBtn.html)
                sendCodeBtn.click(by_js=True)
                logger.info('点击获取验证码')


                yodaBox = page.ele('#yodaBox', timeout=2)
                if yodaBox:
                    logger.info('出现滑块')
                    yodaBox.drag(77, 0, 1.5)
                logger.info(page.html)
                # image_data = page.get_screenshot(as_base64='jpg')
                # sendEmail.send(f'美团：{username}', image_data)

                time.sleep(20)
                smsCode = EmailClient.get_sms_checkCode()

                codeInput = page.ele('#codeInput')
                codeInput.input(smsCode)

                inputChecked = page.ele('#inputChecked')
                inputChecked.click(by_js=True)
                logger.info('点击同意条款')

                iloginBtn = page.ele('#iloginBtn')
                iloginBtn.click(by_js=True)
                logger.info('点击登录按钮')


        except Exception as e:
            logger.error('美团获取token报错：%s', e)
            image_data = page.get_screenshot(as_base64='jpg')
            sendEmail.send(f'用户名：{username},美团获取token报错：{e}', image_data)
        finally:
            page.quit()


