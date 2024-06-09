import os
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

load_dotenv()

def create_token (data_user : dict, time_expires : timedelta| None = None) -> str:
    data_user_copy = data_user.copy()

    if time_expires is None:
        expires = datetime.now(timezone.utc)+timedelta(minutes=1)
    else:
        expires = datetime.now(timezone.utc)+time_expires
    data_user_copy.update({"exp":expires})
    token_jwt = jwt.encode(data_user_copy, key=os.environ.get('SECRET_KEY'), algorithm=os.environ.get('ALGORITHM'))
    return token_jwt