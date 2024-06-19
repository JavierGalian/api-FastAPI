from fastapi import APIRouter, status, Depends, HTTPException
from utils.auth.authenticate_user import authenticate_token_jwt
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from config.db import get_db
from .auth import oauth2_scheme
from models import user_models

email = APIRouter()

@email.post("/authenticate-email", status_code= status.HTTP_200_OK)
async def authenticate_email(token: str,  db : Session = Depends(get_db), token_user_db : Session = Depends(oauth2_scheme)) :
    """
    Endpoint para autenticar un email y activar la cuenta de un usuario.

    Este endpoint permite a un usuario verificar la validez de un token de confirmación de email 
    y, si es válido, activa su cuenta cambiando el campo "is_active" a True en la base de datos.

    Parámetros:
        token (str): Token de confirmación de email enviado al usuario.
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.
        token_user_db (Session): Dependencia utilizada para verificar el token de confirmación de email 
                                   (posiblemente una base de datos o servicio diferente).

    Respuestas:
        200 OK: El token de confirmación es válido y la cuenta del usuario se ha activado. Se devuelve un JSON con un mensaje de confirmación.
        400 Bad Request: El token de confirmación es inválido o ya se ha utilizado.
        500 Internal Server Error: Error interno del servidor al intentar actualizar la base de datos.

    Lógica:
        1. Verifica la validez del token de confirmación de email utilizando la dependencia "token_user_db".
        2. Si el token es válido, recupera la información del usuario utilizando la dependencia "db".
        3. Compara si el usuario obtenido del token de confirmación coincide con el usuario obtenido de la base de datos principal.
        4. Si los usuarios coinciden, actualiza el campo "is_active" del usuario en la base de datos principal a True.
        5. Maneja posibles errores durante la actualización de la base de datos utilizando un bloque try-except.
        6. En caso de éxito, devuelve un JSON con un mensaje de confirmación.

    """

    token_user = authenticate_token_jwt(token, db)
    user_current = authenticate_token_jwt(token_user_db, db)

    if (token_user == user_current):
        user_current_modify = update(user_models.UserModels).where(user_models.UserModels.id==user_current.id).values(is_active = True)
        try:
            db.execute(user_current_modify)
            db.commit()
        except SQLAlchemyError as e:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error: " + str(e)
                )

    return ({"message":"User active"})