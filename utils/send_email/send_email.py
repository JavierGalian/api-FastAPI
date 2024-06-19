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
    Función para crear un objeto de mensaje MIME de tipo texto plano.

    Esta función crea un objeto MIMEText utilizando la librería `email` para representar 
    un mensaje de correo electrónico con contenido de texto plano.

    Parámetros:
        email_addressee (str): Dirección de correo electrónico del destinatario.
        subject (str): Asunto del mensaje.
        message (str): Contenido del mensaje en formato texto plano.

    Respuesta:
        MIMEText: Objeto MIMEText que representa el mensaje de correo electrónico.
    """
    message = MIMEText(message)
    message["from"] = USER_SENDER_EMAIL
    message["to"] = email_addressee
    message["subject"] = subject
    return message

def send_email_to_user(email_addressee: str, message: MIMEText):
    """
    Función para enviar un correo electrónico a un usuario.

    Esta función utiliza el objeto MIMEText creado mediante la funcion 'create_message_to_send' para enviar un 
    correo electrónico al destinatario especificado.

    Parámetros:
        email_addressee (str): Dirección de correo electrónico del destinatario.
        message (MIMEText): Objeto MIMEText que representa el mensaje de correo electrónico.

    Respuesta:
        dict: Diccionario con un mensaje de confirmación ("email sent") 
              en caso de envío exitoso.

    Excepciones:
        HTTPException: Se eleva una excepción HTTP si se produce un error de SMTP 
                       durante el proceso de envío.

    Lógica:
        1. Intenta crear una conexión SMTP:
            - Crea una instancia de `smtplib.SMTP` utilizando las variables 
              globales `SMTP_SERVER` y `SMTP_PORT` (asumiendo que están definidas).
        2. Inicia el protocolo STARTTLS para cifrar la comunicación:
            - Utiliza el método `starttls` para establecer una conexión segura.
        3. Autentica con el servidor SMTP:
            - Utiliza el método `login` para autenticarse con la dirección de correo 
              del remitente (USER_SENDER_EMAIL) y la contraseña (PASSWORD) 
              (asumiendo que están definidas).
        4. Envía el mensaje de correo electrónico:
            - Utiliza el método `sendmail` para enviar el mensaje.
                - Como remitente, se utiliza la dirección de correo del remitente.
                - Como destinatario, se utiliza la dirección de correo proporcionada en "email_addressee".
                - Se convierte el objeto MIMEText a cadena utilizando `as_string()` para su envío.
        5. Manejo de excepciones (SMTPException):
            - Si se produce un error durante el proceso de envío (SMTPException), 
              se eleva una excepción HTTP con un mensaje descriptivo del error.
        6. Cierra la conexión SMTP (dentro del bloque finally):
            - Utiliza el método `quit` para cerrar la conexión con el servidor SMTP 
              independientemente de si hubo éxito o error en el envío.
        7. Retorna un diccionario con un mensaje de confirmación ("email sent").
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