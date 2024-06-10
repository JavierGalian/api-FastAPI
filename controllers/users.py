
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from schemas.user_schemas import UserModelPost, UserModelGet, UserModelPut
from models import user_models
from utils.auth.authenticate_user import get_user_disabled_current, authenticate_token_jwt
from utils.auth.authenticate_email import authenticate_email

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update

from controllers.auth import oauth2_scheme 

users = APIRouter()



#*------------------------------------METHOD GET-----------------------------------------------
# def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     data = db.query(user_models.UserModels).order_by(user_models.UserModels.id).all()
#     return data

# @users.get("/user", status_code=status.HTTP_200_OK)
# async def get_user(users : UserModelGet = Depends(current_user)):
#     return users


@users.get("/user/me", status_code=status.HTTP_200_OK)
async def get_user_me(user : UserModelGet = Depends(get_user_disabled_current)):
    return user

#*------------------------------------METHOD POST-----------------------------------------------
@users.post("/user/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModelPost, db: Session = Depends(get_db)):

    for key, value in user.__dict__.items():
        if value is None:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'data incomplet {key}')
        
    user_data = user.model_dump() #convert user to dictionary

    
    new_user = user_models.UserModels(**user_data)  # Unpack the dictionary

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: " + str(e)
            )

    send_email_user = authenticate_email(**user_data)

    return ({"message": "created ok"}, send_email_user)

#*------------------------------------METHOD PUT-----------------------------------------------

@users.put("/user/update-user", status_code=status.HTTP_200_OK)
async def update_user(user : UserModelPut, db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):

    user_current = authenticate_token_jwt(token, db)

    user_current_modify = update(user_models.UserModels).where(user_models.UserModels.id==user_current.id).values(user.model_dump())
    try:
        db.execute(user_current_modify)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: " + str(e)
            )

    return ({"message":"modify ok"})

#*------------------------------------METHOD DELETE-----------------------------------------------
@users.delete("/user/delete", status_code=status.HTTP_200_OK)
async def delete_user(db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):

    user_current = authenticate_token_jwt(token, db)

    try:
        db.delete(user_current)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: " + str(e)
            )
    
    return ({"message":"ok delete"})