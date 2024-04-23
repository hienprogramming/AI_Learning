import schedule 
import time 
from datetime import datetime, timezone
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

class EmailAutomation:
    def __init__(self, user_mail, password, receiver_mails, subject, img=None, attachment=None, audio=None, timeschedule=None):
        self.user_mail = user_mail
        self.password = password
        self.receiver_mails = receiver_mails
        self.subject = subject
        self.img = img
        self.attachment = attachment
        self.audio = audio
        self.timeschedule = timeschedule
        self.build()

    def build(self):
        mail = MIMEMultipart()
        mail['From'] = self.user_mail
        mail['To'] = ', '.join(self.receiver_mails)
        mail['Subject'] = self.subject

        content = self.write_content()
        mail.attach(MIMEText(content, 'plain'))

        self.attach_images(mail)
        self.attachments(mail)
        self.attach_audio(mail)
        # self.build_schedule()
        self.send(mail)  # Commented out sending directly, as it will be scheduled

    def send(self, mail):
        try:
            server = smtplib.SMTP(host='smtp.gmail.com', port=587)
            server.starttls()
            server.login(user=self.user_mail, password=self.password)
            server.send_message(from_addr=self.user_mail, to_addrs=self.receiver_mails, msg=mail)
            server.quit()
            logging.info("Email sent successfully")
        except smtplib.SMTPException as e:
            logging.error("Failed to send email: %s", e)
    
    def attach_images(self, mail):
        if self.img is not None:
            if isinstance(self.img, str):
                self.img = [self.img]
            for image_path in self.img:
                if os.path.isfile(image_path):
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                    img_name = os.path.basename(image_path)
                    img_mime = MIMEImage(img_data, name=img_name)
                    mail.attach(img_mime)
                else:
                    logging.error(f"Image file not found: {image_path}")
        else:
            pass
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
    def attach_audio(self, mail):
        if self.audio is not None:
            if isinstance(self.audio, str):
                self.audio = [self.audio]
            for audio_path in self.audio:
                if os.path.isfile(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_data = f.read()
                    audio_name = os.path.basename(audio_path)
                    audio_mime = MIMEApplication(audio_data, name=audio_name)
                    audio_mime.add_header('Content-Disposition', 'attachment', filename=audio_name)
                    mail.attach(audio_mime)
                else:
                    logging.error(f"Audio file not found: {audio_path}")
        else:
            pass
    def write_content(self):
        # Extract name part before the "@" symbol
        receiver_names = [email.split('@')[0] for email in self.receiver_mails]
        receivers = ', '.join(receiver_names)
        content = f"Dear {receivers},\n\n"
        content += "I hope this email finds you well. Here is the content of the email.\n\n"
        content += "[Add your main message here.]\n\n"
        content += "Best regards,\n[Your Name]"
        return content

    def build_schedule(self):
        if self.timeschedule is not None:
            schedule.every().day.at(self.timeschedule).do(self.send_scheduled_email)

    def send_scheduled_email(self):
        mail = MIMEMultipart()
        mail['From'] = self.user_mail
        mail['To'] = ', '.join(self.receiver_mails)
        mail['Subject'] = self.subject

        content = self.write_content()
        mail.attach(MIMEText(content, 'plain'))

        self.attach_images(mail)
        self.attachments(mail)
        self.attach_audio(mail)
        self.send(mail)

def checkErrorfile():
    fileError = "D:\\AI\\LearingAI\\ErrorfileExist.txt"
    return os.path.exists(fileError)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    receiver_emails = ['thienanshop2024@gmail.com']
    img = ['C:\\Users\\ADMIN\\Downloads\\Capture.PNG', 'C:\\Users\\ADMIN\\Downloads\\Capture2.PNG']
    attachment = ["D:\\AI\\LearingAI\\AutomationMail.py", "D:\\AI\\LearingAI\\ErrorfileExist.txt"]
    audio = ["C:\\Users\\ADMIN\\Downloads\\HienBach.mp3"]  # Add the path to the audio file here
    
    if checkErrorfile():
        print(f"Check file ErrorfileExist.txt is exist")
        email_automation = EmailAutomation('bachhien500@gmail.com',
                                           'swwa frgx lzkc quqf',
                                           receiver_emails,
                                           'TEST Timeschedule',
                                           img,
                                           attachment,
                                           # audio,
                                           # timeschedule="22:41"
                                          )
        current_time = datetime.now()
        print(f"Time send email is: {current_time}")

        # Using for loop to run timeschedule
        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)
    
    else:
        print("Check file ErrorfileExist.txt does not exist!")
