from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import logging
import smtplib
import os

'''
    - def build
    - def send
    - def message
    - def image
    - def audio
    - def attach file
'''

class EmailAutomation:
    def __init__(self, username, password, receiver_names, Subject, \
                 attachment):
        self.username = username
        self.password = password
        self.receiver_names = receiver_names
        self.Subject = Subject
        self.attachment = attachment
        self.build()

    def build(self):
        mail = MIMEMultipart()
        mail["From"] = self.username
        mail['To'] = self.receiver_names    # for more email
        mail['Subject'] = self.Subject

        self.send(mail)
        self.attachments(mail)

    def send(self, mail):
        try:
            server = smtplib.SMTP(host='smtp.gmail.com', port=587)
            server.starttls()
            server.login(user=self.username, password=self.password)
            server.send_message(from_addr=self.username, to_addrs=self.receiver_names, msg=mail)
            # server.quit()
            logging.info("Email sent successfully")
        except smtplib.SMTPException as e:
            logging.error("Failed to send email: %s", e)


    def attachments(self, mail):
        if self.attachment is not None:
            if isinstance(self.attachment, str):
                self.attachment = [self.attachment]
            for one_attachment in self.attachment:
                if os.path.isfile(one_attachment):
                    with open(one_attachment, 'rb') as f:
                        file = MIMEApplication(f.read(), name=os.path.basename(one_attachment))
                    file.add_header('Content-Disposition', 'attachment', filename=os.path.basename(one_attachment))
                    mail.attach(file)
                else:
                    logging.error(f"Attachment file not found: {one_attachment}")
        else:
            pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    username = "bachhien500@gmail.com"
    password = "swwa frgx lzkc quqf"
    receiver_names = "thienanshop2024@gmail.com"
    Subject = "hahaha"
    attachment = ["D:\\AI\\LearingAI\\AutomationMail.py", "D:\\AI\\LearingAI\\ErrorfileExist.txt"]
    email_automation = EmailAutomation(username, password, receiver_names, \
                           Subject, attachment)
    
    
