import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.mail.sender_client import SenderClient


class SMTPClient(SenderClient):

    def __init__(self):
        super().__init__()
        smtp_server = "smtp.rambler.ru"
        smtp_port = 465
        self.smtp_connection = smtplib.SMTP_SSL(smtp_server, smtp_port)
        self.smtp_connection.ehlo()
        self.smtp_connection.login(self.username, self.password)

    def send(self, from_user: str, to_user: str, subject: str, text: str, files: list = None):
        message = MIMEMultipart()
        message["From"] = from_user
        message["To"] = to_user
        message["Subject"] = subject
        message.attach(MIMEText(text, "plain"))

        if files:
            for file_path in files:
                with open(file_path, "rb") as file:
                    attachment = MIMEApplication(file.read())

                    attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=file.name
                    )
                    message.attach(attachment)

        self.smtp_connection.send_message(message)
        return message

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtp_connection.quit()
