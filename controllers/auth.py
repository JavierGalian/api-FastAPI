
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from models import user_models

from utils.auth.create_token import create_token

from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

user_auth = APIRouter()


@user_auth.post("/api/user/login" , status_code=status.HTTP_200_OK)
async def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint para iniciar sesión de un usuario en la API.

    Este endpoint permite a los usuarios autenticarse utilizando su nombre de usuario y contraseña. 
    Si la autenticación es exitosa, se devuelve un token JWT para ser utilizado en solicitudes posteriores 
    que requieran autorización.

    Parámetros:
        user (OAuth2PasswordRequestForm): Objeto que contiene el nombre de usuario y contraseña del usuario 
                                          proporcionados en la solicitud. 
                                          (Este objeto proviene de la dependencia OAuth2PasswordRequestForm).
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas.

    Respuestas:
        200 OK: Autenticación exitosa. Se devuelve un JSON con el token de acceso y el tipo de token ("Bearer").
        400 Bad Request: Error en la solicitud. Se devuelve un JSON con un mensaje de error indicando 
                         si el nombre de usuario o la contraseña son incorrectos.

    Ejemplo de uso:
        curl -X POST "[se quitó una URL no válida]api/user/login" -H "Content-Type: application/json" -d '{"username": "micuentadeusuario", "password": "micontraseña"}'
    """

    ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(hours = 1)

    user_data = db.query(user_models.UserModels).filter(user_models.UserModels.username == user.username).first()

    if user_data:
        if user_data.verify_password(user.password):
            access_token_jwt = create_token({"sub" : user_data.username}, ACCESS_TOKEN_EXPIRE_MINUTES)
            return {
                    "access_token": access_token_jwt,
                    "type_token":"Bearer"
                    }
        else:
            return {"error":"password is incorrect"}
    return {"error":"username is incorrect"}