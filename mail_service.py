import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailService:
    def __init__(self, imap_server, smtp_server, user, password):
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.user = user
        self.password = password
        self.connection = None

    def imap_connect(self):
        # 连接到IMAP服务器
        self.imap_connection = imaplib.IMAP4_SSL(self.imap_server)
        self.imap_connection.login(self.user, self.password)

    def receive_mails(self, sender, days=7, max_mails=10):
        if self.imap_connection is None:
            self.imap_connect()
        # 选择"Inbox"文件夹
        self.imap_connection.select("inbox")

        # 定义搜索的日期范围
        date_since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")

        # 搜索特定发送人在过去n天内发送的邮件
        status, messages = self.imap_connection.search(None, f'(FROM "{sender}" SINCE {date_since})')

        email_bodies = []

        # 确保我们有搜索结果
        if status == "OK":
            # 转换messages为邮件ID列表
            messages = messages[0].split()

        # 取最新的max_mails封邮件
        for mail_id in messages[-max_mails:]:
            status, data = self.imap_connection.fetch(mail_id, "(RFC822)")
            # 解析邮件内容
            message = email.message_from_bytes(data[0][1])

            # 解码邮件信息
            subject, encoding = decode_header(message["Subject"])[0]
            if isinstance(subject, bytes):
                # 如果它是一个字节字符串，解码这个字符串
                subject = subject.decode(encoding)

            from_, encoding = decode_header(message.get("From"))[0]
            if isinstance(from_, bytes):
                from_ = from_.decode(encoding)

            # 获取邮件发送日期
            date_hdr = message.get('Date')
            if date_hdr:
                try:
                    date = parsedate_to_datetime(date_hdr)
                    weekday_name = date.strftime("%A")
                    date_str = date.strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Error parsing date: {e}")

            # 打印邮件信息
            print("Subject:", subject)
            print("From:", from_)
            print("Date:", date_str)
            print("weekday:", weekday_name)
            # 如果邮件内容是multipart类型
            if message.is_multipart():
                for part in message.walk():
                    # 提取内容类型
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    try:
                        # 获取邮件内容
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # 打印 text/plain 邮件内容
                        print(body)
                        email_bodies.append(date_str + " " + weekday_name + " " + body)
                    elif "attachment" in content_disposition:
                        continue
            else:
                # 如果邮件内容不是multipart类型
                content_type = message.get_content_type()
                body = message.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    email_bodies.append(date_str + " " + weekday_name + " " + body)
                    print(body)

            print("=" * 100)
        # 返回邮件正文列表
        return email_bodies

    def imap_close(self):
        if self.imap_connection is not None:
            self.imap_connection.logout()

    def smtp_connect(self):
        # 连接到SMTP服务器
        self.smtp_connection = smtplib.SMTP(self.smtp_server, 587)
        self.smtp_connection.starttls()
        self.smtp_connection.login(self.user, self.password)

    def send_mail(self, subject, recipients, body):
        # 确保已经建立了连接
        if self.smtp_connection is None:
            self.smtp_connect()

        # 创建MIMEText对象
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.user
        message["To"] = recipients

        # 邮件正文内容
        part = MIMEText(body, "plain")
        message.attach(part)
        # 发送邮件
        try:
            self.smtp_connection.sendmail(self.user, recipients.split(','), message.as_string())
            print("邮件成功发送！")
        except Exception as e:
            print(f"邮件发送失败: {e}")

    def smtp_close(self):
        if self.smtp_connection is not None:
            self.smtp_connection.quit()
