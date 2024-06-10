import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from smtplib import SMTPException
from fastapi import HTTPException

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USER_SENDER_EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("PASSWORD_APP")

def create_message_to_send(email_addressee: str, subject: str, message: str)->MIMEText:
    """
    Create message return data MIMEText type
    """
    message = MIMEText(message)
    message["from"] = USER_SENDER_EMAIL
    message["to"] = email_addressee
    message["subject"] = subject
    return message

def send_email_to_user(email_addressee: str, message: MIMEText):
    """
    send email to user
    """
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USER_SENDER_EMAIL, PASSWORD)
        server.sendmail(USER_SENDER_EMAIL, email_addressee, message.as_string())
    except SMTPException as e:
        raise HTTPException(f"Error de SMTP: {e}")
    finally:
        server.quit()
    return{"message":"email sent"}