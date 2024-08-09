import poplib
import time
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import yaml

from commonUtils.log import logger


# 定义EmailClient类，用于连接到POP3服务器并从指定的邮件地址获取邮件
class EmailClient:
    # 在初始化函数中，设置POP3服务器的来源、用户、密码和待查询的目标邮件地址
    def __init__(self, host, user, password, target_email):
        self.pop_server = poplib.POP3_SSL(host)  # 使用POP3协议通过SSL安全连接到邮件服务器
        self.pop_server.user(user)  # 输入用户邮箱
        self.pop_server.pass_(password)  # 输入用户邮箱密码
        self.target_email = target_email  # 输入待查询的目标邮件地址

    # 定义一个函数，用以清除文件名中的无效字符
    def sanitize_folder_name(self, name):
        invalid_characters = "<>:\"/\\|?*@"
        for char in invalid_characters:  # 遍历所有无效字符
            name = name.replace(char, "_")  # 将无效字符替换为下划线
        return name  # 返回清理后的名称

    # 定义一个函数，用以提取邮件的payload（有效载荷，即邮件主体内容）
    def get_payload(self, email_message):
        if email_message.is_multipart():  # 判断邮件是否为多部分邮件
            for part in email_message.iter_parts():  # 如果是，则遍历其中的每一部分
                content_type = part.get_content_type()  # 获取该部分的内容类型
                if content_type == 'text/html':  # 如果内容类型为HTML，则返回该部分内容
                    return part.get_content()
                elif content_type == 'text/plain':  # 如果内容类型为纯文本，则返回该部分内容
                    return part.get_content()
                # 如果内容类型是multipart/alternative，进一步解析
                elif content_type == 'multipart/alternative':
                    for subpart in part.get_payload():
                        # 根据内容类型选择解码方式
                        if subpart.get_content_type() == 'text/plain':
                            # 获取纯文本内容
                            text = subpart.get_payload(decode=True).decode(subpart.get_content_charset())
                            return text
                        elif subpart.get_content_type() == 'text/html':
                            # 获取HTML内容
                            html = subpart.get_payload(decode=True).decode(subpart.get_content_charset())
                            print('HTML内容:', html)
        elif email_message.get_content_type() == 'text/html':  # 如果邮件非多部分形式，且为HTML类型，则返回邮件内容
            return email_message.get_content()
        elif email_message.get_content_type() == 'text/plain':  # 如果邮件非多部分形式，且为纯文本类型，则返回邮件内容
            return email_message.get_content()

    # 定义一个函数，用以获取邮件信息
    def fetch_last_email(self):

        # 查找匹配的邮件
        for i in range(2):
            num_emails = len(self.pop_server.list()[1])  # 获取邮箱内的邮件数量
            # 获取邮件内容
            response, lines, octets = self.pop_server.retr(num_emails)  # retr函数返回指定邮件的全部文本
            email_content = b'\r\n'.join(lines)  # 将所有行连接成一个bytes对象

            # 解析邮件内容
            email_parser = BytesParser(policy=policy.default)  # 创建一个邮件解析器
            email = email_parser.parsebytes(email_content)  # 解析邮件内容，返回一个邮件对象

            # 解析邮件头部信息并提取发件人信息
            email_from = email.get('From').strip()  # 获取发件人信息，并去除尾部的空格
            email_from = str(make_header(decode_header(email_from)))  # 解码发件人信息，并将其转换为字符串
            if email_from == self.target_email:  # 如果发件人地址与指定的目标邮件地址一致，对邮件进行处理
                # 解析邮件时间
                email_time = email['Date']  # 获取邮件时间
                if email_time:
                    logger.info('获取到匹配的邮件，接收时间：{}'.format(parsedate_to_datetime(email_time)))

                # 提取邮件正文
                email_body = self.get_payload(email)  # 获取邮件正文

                return email_body  # 返回邮件正文
            #最新一封不是想要的，等待后再尝试
            logger.info('最新一封不是想要的，等待后再尝试')
            time.sleep(20)

        print("No new emails from", self.target_email)  # 如果没有从目标邮件地址收到新邮件，打印相应信息
        return None, None  # 返回None

        # 定义一个函数，用以获取邮件信息
    def quit(self):
        self.pop_server.quit()

    #获取短信验证码
    @staticmethod
    def get_sms_checkCode():
        with open('config/config.yml', 'r', encoding='utf-8') as f:
            configs = yaml.load(f, Loader=yaml.FullLoader)
        password = configs['sendEmail']['password']
        client = EmailClient('pop.qq.com', '996335280@qq.com', password, '阿宇 <996335280@qq.com>')
        body = client.fetch_last_email()
        print("email Body:", body)
        # 断开连接
        client.quit()
        if body:
            return body.split('\n')[0]
        return None


#EmailClient.get_sms_checkCode()