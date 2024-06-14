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