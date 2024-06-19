from .create_token import create_token
from ..send_email.send_email import create_message_to_send, send_email_to_user
from datetime import timedelta


def authenticate_email(**kwargs: dict):
    """
    Función para autenticar un usuario mediante correo electrónico.

    Esta función presumiblemente se utiliza para enviar un código de verificación 
    o enlace de activación al correo electrónico proporcionado por el usuario 
    durante el registro o algún proceso de recuperación de credenciales.

    Parámetros:
        kwargs (dict): Diccionario que contiene información del usuario, 
                     generalmente incluyendo la clave "email" (correo electrónico).

    Respuesta:
        (opcional): Depende de la implementación de `send_email_to_user`. 
                    - Podría retornar True o False indicando el éxito del envío.
                    - Podría retornar un identificador del mensaje enviado.
                    - Podría no retornar ningún valor.

    Lógica:
        1. Define el tiempo de expiración del token de acceso 
           (ACCESS_TOKEN_EXPIRE_MINUTES).
        2. Crea un token JWT utilizando la función `create_token`. 
           - El token contendrá el campo "sub" con el nombre de usuario 
             obtenido del diccionario "kwargs".
           - El token tendrá una validez definida por `ACCESS_TOKEN_EXPIRE_MINUTES`.
        3. Construye el mensaje a enviar al usuario:
           - Combina un texto introductorio ("Codigo de verificacion") 
             con el token JWT generado en el paso 2.
        4. Crea un mensaje de correo electrónico utilizando `create_message_to_send`.
           - Define el destinatario (correo electrónico) obtenido de "kwargs".
           - Define el asunto del mensaje ("Codigo de verificacion").
           - Define el cuerpo del mensaje utilizando la variable "message_to_user".
        5. Envía el mensaje de correo electrónico utilizando `send_email_to_user`.
           - El comportamiento de esta función y su valor de retorno 
             dependen de su implementación específica.
    """

    ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes = 30)
    token_jwt = create_token({"sub" : kwargs.get("username")}, ACCESS_TOKEN_EXPIRE_MINUTES)
    
    message_to_user = "Codigo de verificacion" + token_jwt 
    message_subject = "Codigo de verificacion"
    message = create_message_to_send(kwargs.get("email"), message_subject, message_to_user)
    return send_email_to_user(kwargs.get("email"), message)