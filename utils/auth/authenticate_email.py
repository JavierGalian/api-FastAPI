from .create_token import create_token
from ..send_email.send_email import create_message_to_send, send_email_to_user
from datetime import timedelta


def authenticate_email(**kwargs: dict):
    """
    Authenticate user with email
    **kwargs: dictionary
    """

    ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes = 30)
    token_jwt = create_token({"sub" : kwargs.get("username")}, ACCESS_TOKEN_EXPIRE_MINUTES)
    
    message_to_user = "Codigo de verificacion" + token_jwt 
    message_subject = "Codigo de verificacion"
    message = create_message_to_send(kwargs.get("email"), message_subject, message_to_user)
    return send_email_to_user(kwargs.get("email"), message)