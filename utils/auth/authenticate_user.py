import os
from dotenv import load_dotenv

from controllers.auth import oauth2_scheme
from config.db import get_db
from models import user_models
from schemas.user_schemas import UserModelGet

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from jose import jwt, JWTError

load_dotenv()

def authenticate_token_jwt(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Función para autenticar a un usuario mediante un token JWT.

    Esta función valida el token JWT proporcionado por el usuario en la solicitud 
    y devuelve la información del usuario asociado al token si es válido.

    Parámetros:
        token (str, optional): Token JWT obtenido de la dependencia "oauth2_scheme".
        db (Session, optional): Dependencia que inyecta una sesión de la base de datos.

    Respuesta:
        user_models.UserModels: Objeto del modelo UserModels que representa al usuario autenticado.

    Excepciones:
        HTTPException: Se eleva una excepción HTTP con código 400 (Bad Request) 
                      y detalles de error si:
            - El token JWT es inválido (JWTError).
            - El token no contiene el campo "sub" (identificador de usuario).
            - El usuario asociado al token no se encuentra en la base de datos.

    Lógica:
        1. Intenta decodificar el token JWT:
            - Utiliza la librería `jwt` para decodificar el token.
            - La clave secreta para la decodificación se obtiene de la variable de entorno "SECRET_KEY".
            - Se especifican los algoritmos de firma permitidos por la variable de entorno "ALGORITHM".
        2. Manejo de errores de decodificación (JWTError):
            - Si se produce un error durante la decodificación, se eleva una excepción HTTP 400 
              indicando "error de credenciales".
        3. Extrae el identificador de usuario ("sub") del token decodificado.
        4. Valida si el identificador de usuario está presente en el token:
            - Si el campo "sub" es nulo, se eleva una excepción HTTP 400 
              indicando "error de credenciales".
        5. Consulta la base de datos para obtener el usuario:
            - Realiza una consulta a la base de datos utilizando la sesión "db".
            - Filtra la tabla "user_models.UserModels" por el campo "username" 
              igual al identificador de usuario obtenido del token.
            - Utiliza el método "first()" para recuperar el primer usuario 
              que coincida con el criterio de búsqueda.
        6. Valida si se encontró el usuario en la base de datos:
            - Si la consulta no devuelve ningún usuario ("not user"), se eleva una excepción HTTP 400 
              indicando "error de credenciales".
        7. Si la validación es exitosa, retorna el objeto del modelo "user_models.UserModels" 
           que representa al usuario autenticado.
    """

    try:
        token_decode = jwt.decode(token, key=os.environ.get('SECRET_KEY'), algorithms=os.environ.get('ALGORITHM'))
        username = token_decode.get("sub")
        if username == None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error de credenciales", headers={"WWW-Authenticate":"Bearer"})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error de credenciales", headers={"WWW-Authenticate":"Bearer"})

    user = db.query(user_models.UserModels).filter(user_models.UserModels.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error de credenciales", headers={"WWW-Authenticate":"Bearer"})
    return user

def get_user_disabled_current(user: UserModelGet = Depends(authenticate_token_jwt)):
    """
    Función para verificar si el usuario autenticado está activo.

    Esta función espera recibir el usuario autenticado a través de la dependencia 
    "authenticate_token_jwt". Luego, verifica el estado de activación del usuario 
    y devuelve el usuario si está activo.

    Parámetros:
        user (UserModelGet, optional): Dependencia que inyecta el usuario autenticado 
                                       obtenido de la función "authenticate_token_jwt".

    Respuesta:
        user_models.UserModels: Objeto del modelo UserModels que representa al usuario autenticado 
                               y activo.

    Excepciones:
        HTTPException: Se eleva una excepción HTTP con código 400 (Bad Request) 
                      y detalles de error si el usuario autenticado no está activo.
    """
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="usuario inactivo", headers={"WWW-Authenticate":"Bearer"})
    return user