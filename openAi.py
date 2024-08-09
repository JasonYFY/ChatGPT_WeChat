# -*- coding: utf-8 -*-
import json
import time

from DrissionPage import WebPage, ChromiumOptions

from commonUtils.log import logger
from sendEmail import sendEmail


class openAi:

    @staticmethod
    def getAccessToken(username: str, password: str, type: str):
        global page
        logger.info('获取gpt的token,用户名：{},类型：{}'.format(username, type))
        if not username:
            raise Exception('invalid username.')
        if not password:
            raise Exception('invalid password.')
        try:

            # co = ChromiumOptions().set_paths(local_port=9222)
            co = ChromiumOptions().set_paths(local_port=9211,browser_path=r'/opt/google/chrome/google-chrome',user_data_path=r'/tmp/DrissionPage/userData_9211')
            co.set_argument('--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            # 设置用隐身模式启动浏览器
            co.set_argument('--incognito')
            co.set_argument('--no-sandbox')
            co.set_argument('--headless')
            co.set_timeouts(implicit=20)
            # 创建页面对象，并启动或接管浏览器
            page = WebPage(driver_or_options=co)
            # 跳转到登录页面
            page.get('https://chat.openai.com/chat')
            logger.info('打开页面了')

            # #判断是否进入了cf
            # i = page.ele('tag:iframe@src^https://challenges.cloudflare.com/cdn-cgi')
            # # 判断是否找到元素
            # if i:
            #     # page.screencast.set_mode.video_mode()
            #     # page.screencast.set_save_path('video')  # 设置视频存放路径
            #     # page.screencast.start()
            #     logger.info('证明进入cf')
            #     i = page.get_frame(i)
            #     e = i('.mark')
            #     logger.info('出现了cf验证')
            #     time.sleep(3)
            #     for i in range(20):
            #         e.click()
            #         time.sleep(2)
            #     logger.info('点击了cf验证')
            #     time.sleep(3)
            #     # page.screencast.stop()


            # 1.等待登录按钮的出现，然后点击
            # loginBtn = page.ele('@data-testid=login-button')
            loginBtn = page.ele('text=Log in')
            loginBtn.click(by_js=True)
            logger.info('点击了登录按钮')

            # usernameEle = None
            if type and type == 'micro':
                # 2.点击微软按钮
                microsBtn = page.ele('tag:span@text():Microsoft Account')
                microsBtn.click(by_js=True)
                logger.info('点击了微软按钮')
                usernameEle = page.ele('tag:input@@type=email@@name=loginfmt')
                # 3.输入用户名并点击下一步按钮
                usernameEle.input(username)
                nextBtn = page.ele('#idSIButton9')
                nextBtn.click(by_js=None)
                logger.info('点击了下一步按钮')

                # 4.输入密码并点击登录按钮
                page.wait.ele_display('#idA_PWD_ForgotPassword')
                logger.info('出现了密码框')
                passwordEle = page.ele('tag:input@@type=password@@name=passwd')
                passwordEle.input(password)
                loginBtn = page.ele('#idSIButton9')
                loginBtn.click(by_js=None)
                logger.info('点击了最终登录按钮')

                # 5.点击下一步按钮
                # page.wait.ele_display('#idBtn_Back')
                # page.wait.ele_display('#KmsiDescription')
                #page.wait.ele_display('tag:input@type=submit')
                # yesBtn = page.ele('#acceptButton')
                yesBtn = page.ele('tag:button@|text()=是@|text()=Yes')
                yesBtn.click(by_js=None)
                logger.info('点击了是按钮')
            else:
                page.ele('tag:h1@class=title')
                logger.info('跳转到了登录页面')
                # logger.info(page.html)
                # usernameEle = page.ele('#email-input')
                usernameEle = page.ele('tag:label@text():Email address').parent().ele('tag:input')
                logger.info('找到输入框了：%s', usernameEle.html)
                usernameEle.input(username)
                logger.info('输入了账户名')
                nextBtn = page.ele('tag:button@|text()=继续@|text()=Continue')
                nextBtn.click(by_js=None)
                logger.info('点击了继续按钮')

                passwordEle = page.ele('#password')
                passwordEle.input(password)
                loginBtn = page.ele('tag:button@@type=submit@@name=action')
                loginBtn.click(by_js=None)
                logger.info('点击了最终登录按钮')

            # page.get_screenshot('gpt_login2.png')

            page.wait.set_targets('chat.openai.com/api/auth/session', is_regex=False)
            res = page.wait.data_packets(any_one=True)
            # logger.info(res.response)
            logger.info(res.body)
            # logger.info(res.postData)

            data = res.body
            return data["accessToken"]
        except Exception as e:
            logger.error('getAccessToken报错：%s', e)
            image_data = page.get_screenshot(as_base64='jpg')
            sendEmail.send(f'用户名：{username},获取gpt的token报错：{e}', image_data)
        finally:
            page.quit()
