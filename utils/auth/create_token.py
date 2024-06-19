import os
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

load_dotenv()

def create_token (data_user : dict, time_expires : timedelta| None = None) -> str:
    """
    Función para crear un token JWT.

    Esta función genera un token JSON Web Token (JWT) utilizando la información 
    proporcionada en el diccionario "data_user".

    Parámetros:
        data_user (dict): Diccionario que contiene los datos del usuario a incluir en el token.
        time_expires (timedelta, optional): Objeto timedelta que define el tiempo de expiración del token. 
                                             Si no se especifica, se establece un valor predeterminado de 1 minuto.

    Respuesta:
        str: Cadena que representa el token JWT generado.

    Lógica:
        1. Crea una copia del diccionario "data_user" para evitar modificaciones del original.
        2. Determina el tiempo de expiración del token:
            - Si se proporciona un valor de "time_expires" (timedelta), lo utiliza directamente.
            - Si no se especifica "time_expires", establece un valor predeterminado de 1 minuto.
        3. Calcula la fecha y hora de expiración del token:
            - Obtiene la fecha y hora actual en UTC utilizando "datetime.now(timezone.utc)".
            - Suma el valor de "time_expires" (o el valor predeterminado) a la fecha y hora actual.
        4. Crea un diccionario temporal ("data_user_copy") e incluye los datos del usuario:
            - Copia los datos del diccionario "data_user" original.
            - Agrega un campo "exp" (expiración) al diccionario temporal, 
              asignándole la fecha y hora de expiración calculada en el paso 3.
        5. Genera el token JWT:
            - Utiliza la librería `jwt` para codificar el diccionario temporal "data_user_copy".
            - La clave secreta para la codificación se obtiene de la variable de entorno "SECRET_KEY".
            - Se especifica el algoritmo de firma permitido por la variable de entorno "ALGORITHM".
        6. Retorna la cadena que representa el token JWT generado.
    """

    data_user_copy = data_user.copy()

    if time_expires is None:
        expires = datetime.now(timezone.utc)+timedelta(minutes=1)
    else:
        expires = datetime.now(timezone.utc)+time_expires
    data_user_copy.update({"exp":expires})
    token_jwt = jwt.encode(data_user_copy, key=os.environ.get('SECRET_KEY'), algorithm=os.environ.get('ALGORITHM'))
    return token_jwt