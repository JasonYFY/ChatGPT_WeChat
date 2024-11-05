# -*- coding: utf-8 -*-

import time
from typing import List

from DrissionPage import ChromiumPage, ChromiumOptions

from commonUtils.log import logger
from sendEmail import sendEmail


class signIn:

    @staticmethod
    def singInOfHuaxiashuyu(username: str, password: str):
        global page
        logger.info('用户名：{}'.format(username))
        if not username:
            raise Exception('invalid username.')
        if not password:
            raise Exception('invalid password.')
        try:

            # co = ChromiumOptions().set_paths(browser_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
            # co = ChromiumOptions().set_paths(local_port=9111,browser_path=r'/opt/microsoft/msedge-dev/microsoft-edge',user_data_path=r'/tmp/DrissionPage/userData_9111')
            co = ChromiumOptions().set_paths(local_port=9211, browser_path=r'/opt/google/chrome/google-chrome',
                                             user_data_path=r'/tmp/DrissionPage/userData_9211')
            # 设置用隐身模式启动浏览器
            # co.set_argument('--incognito')
            # co.set_argument('--no-sandbox')
            # co.set_argument('--disable-plugins-discovery')
            co.set_argument('--headless')
            co.set_timeouts(implicit=20)
            # 创建页面对象，并启动或接管浏览器
            page = ChromiumPage(addr_driver_opts=co)
            page.get('https://www.huaxiashuyu.com/')
            logger.info('打开页面了')

            # 是否有弹出框
            swal = page.ele('#swal2-content', timeout=2)
            if swal:
                logger.info('有弹出框，关闭弹框')
                close = page.ele('tag:button@class=swal2-close')
                close.click(by_js=True)

            loginBtn = page.ele('tag:div@class=login-btn navbar-button', timeout=2)
            if loginBtn:
                logger.info('未登录')
                loginBtn.click(by_js=True)
                usernameInput = page.ele('tag:input@name=username')
                usernameInput.input(username)
                passwordInput = page.ele('tag:input@name=password')
                passwordInput.input(password)
                login = page.ele('tag:button@class:go-login')
                login.click(by_js=True)
                logger.info('登录成功')

            page.ele('tag:a@class=user-pbtn')
            burger = page.ele('tag:div@class=burger')
            burger.click(by_js=True)

            # page.get_screenshot('singInOfHuaxiashuyu.png')
            hand = page.ele('tag:i@class:fa-hand-peace-o', timeout=3)

            if hand:
                logger.info('证明未签到')
                # click-qiandao btn btn-qiandao
                qiandao = page.ele('tag:button@class:btn-qiandao')
                qiandao.click(by_js=True)
                time.sleep(2)
                logger.info('签到成功')
                return
            logger.info('显示已签到')

        except Exception as e:
            logger.error('singInOfHuaxiashuyu报错：%s', e)
            image_data = page.get_screenshot(as_base64='jpg')
            sendEmail.send(f'用户名：{username},签到花夏数娱报错：{e}', image_data)
        finally:
            page.quit()

    @staticmethod
    def singInOfTgHelp(sendText: List[str]):
        global page
        logger.info('发送的文字：{}'.format(sendText))
        if not sendText:
            raise Exception('Invalid sendText. The list is empty.')
        try:

            # co = ChromiumOptions().set_paths(browser_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
            co = ChromiumOptions().set_paths(local_port=9211, browser_path=r'/opt/google/chrome/google-chrome',
                                             user_data_path=r'/tmp/DrissionPage/userData_9211')
            co.set_argument('--headless')
            co.set_timeouts(implicit=20)
            # 创建页面对象，并启动或接管浏览器
            page = ChromiumPage(addr_driver_opts=co)
            page.get('https://web.telegram.org/a/#5479559602')
            logger.info('打开页面了')
            time.sleep(3)
            # 第一次，需要登录才行 ，截图
            for i in range(3):
                swal = page.ele('#auth-qr-form', timeout=2)
                if swal:
                    time.sleep(3)
                    # 等待二维码出来
                    page.ele('tag:div@class=qr-container').ele('tag:svg')
                    logger.info('需要登录，准备截图发送')
                    image_data = page.get_screenshot(as_base64='jpg')
                    sendEmail.send('请扫码登录：', image_data)
                    logger.info('睡眠60s')
                    time.sleep(60)
                else:
                    logger.info('应该登录成功了')
                    break
            # 重新打开这个页面
            # abtn = page.ele('tag:a@href=#5479559602')
            # abtn.click(by_js=True)

            #page.get('https://web.telegram.org/a/#5479559602')
            logger.info('打开了相应的聊天界面')

            for text in sendText:
                message = page.ele('#editable-message-text')
                message.input(text)

                send = page.ele('tag:button@title=Send Message')
                send.click(by_js=True)
                logger.info('发送文字成功: %s', text)
                time.sleep(2)

            # page.get_screenshot('singInOfTgHelp.png')

        except Exception as e:
            logger.error('singInOfTgHelp报错：%s', e)
            image_data = page.get_screenshot(as_base64='jpg')
            sendEmail.send(f'发送的文字：{sendText},发送tg报错：{e}', image_data)
        finally:
            try:
                page.quit()
            except Exception as e:
                logger.debug('singInOfTgHelp退出浏览器正常报错，不用理：%s', e)

