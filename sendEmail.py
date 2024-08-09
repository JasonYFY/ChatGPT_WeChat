import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml

from commonUtils.log import logger


class sendEmail:
    # 设置发件人、收件人、主题和正文
    sender_email = '996335280@qq.com'
    receiver_email = '996335280@qq.com'
    subject = '通知邮件'

    # 设置发件人邮箱的用户名和密码
    username = '996335280@qq.com'

    with open('config/config.yml', 'r', encoding='utf-8') as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
    password = configs['sendEmail']['password']

    @staticmethod
    def send(body: str, image_data: str):

        # 设置 SMTP 服务器和端口
        smtp_server = 'smtp.qq.com'
        smtp_port = 587

        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = sendEmail.sender_email
        msg['To'] = sendEmail.receiver_email
        msg['Subject'] = sendEmail.subject


        # # 读取图片文件并进行 base64 编码
        # with open(image_path, 'rb') as image_file:
        #     image_data = base64.b64encode(image_file.read()).decode('utf-8')

        if image_data:
            # 构建 HTML 内容
            html_content = """
            <html>
                <body>
                    <p>{0}</p>
                    <p><img src="data:image/jpeg;base64,{1}" alt="resized_image"  style="max-height: 300px; width: auto;"></p>
                </body>
            </html>
            """.format(body, image_data)
            # 将正文添加到邮件中
            msg.attach(MIMEText(html_content, 'html'))
        else:
            # 将正文添加到邮件中
            msg.attach(MIMEText(body, 'plain'))


        # 附加图片文件
        # if image_path:
        #     # 拼接图片文件的完整路径
        #     image_path = os.path.join(os.getcwd(), image_path)
        #     logger.info('发送邮件图片路径：{}'.format(image_path))
        #     with open(image_path, 'rb') as image_file:
        #         image_data = image_file.read()
        #         image = MIMEImage(image_data)
        #         image.add_header('Content-Disposition', 'inline', filename='image.jpg')
        #         msg.attach(image)

        # 创建 SMTP 连接
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # 使用 TLS 加密连接
            server.starttls()

            # 登录发件人邮箱
            server.login(sendEmail.username, sendEmail.password)

            # 发送邮件
            server.sendmail(sendEmail.sender_email, sendEmail.receiver_email, msg.as_string())

        logger.info('发送邮件成功!')