from mail_service import MailService
from summarize import KindergartenSummarizer
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(verbose=True)

    imap_server = "imap.gmail.com"
    smtp_server = "smtp.gmail.com"
    user = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    sender_email_user = os.getenv('SENDER_EMAIL_USER')

    if not user or not password or not sender_email_user:
        raise ValueError("EMAIL_USER and EMAIL_PASS and SENDER_EMAIL_USER must be set as environment variables.")

    mail_service = MailService(imap_server, smtp_server, user, password)

    # メール検索
    mail_service.imap_connect()
    email_bodies = mail_service.receive_mails(sender_email_user)
    mail_service.imap_close()

    print(email_bodies)

    # check if email_bodies is empty
    if not email_bodies:
        print("No emails to summarize.")
        exit(0)

    # メールまとめ
    summarizer = KindergartenSummarizer()
    response_text = summarizer.summarize_emails(email_bodies)

    print(response_text)
    # まとめた内容送信
    subject = "幼稚園週まとめ"
    recipient = os.getenv('TARGET_EMAIL_USERS')
    mail_service.smtp_connect()
    mail_service.send_mail(subject, recipient, response_text)
    mail_service.smtp_close()
