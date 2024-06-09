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
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="usuario inactivo", headers={"WWW-Authenticate":"Bearer"})
    return user