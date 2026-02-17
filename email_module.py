import smtplib
from email.mime.text import MIMEText

class Email:
    def __init__(self, recipient_email):
        self.sender = "kfgggh60@gmail.com"
        self.password = "juzq rmnj mhzu uumx"
        self.recipient = recipient_email


    def verify_email(self, message):
        """Функция отправки email"""
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender, self.password)

                msg = MIMEText(message)
                msg["Subject"] = "Verify email"
                msg["From"] = self.sender
                msg["To"] = self.recipient

                server.sendmail(self.sender, self.recipient, msg.as_string())

            return "порука послана успешно"
        except Exception as _ex:
            print(_ex)
            return f"грешка, ми неможемо да пошаљемо поруку на ваш email"