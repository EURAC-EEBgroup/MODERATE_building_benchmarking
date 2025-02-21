from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
import typing as t
import os

from app.definitions import APP_CLIENTID, APP_SECRET

# to get a string like this run:
# openssl rand -hex 32
API_SECRET_KEY = os.environ.get('API_SECRET_KEY', "b8e10f0cb4480ddbeb428bd41ae8e45d8265fa27c1437ebdb8bd5adbd1673324")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


class User():
    clientid: str
    secret: str


def find_user(clientid: str):
    if clientid == APP_CLIENTID:
        user = User()
        user.clientid = APP_CLIENTID
        user.secret = get_password_hash(APP_SECRET)
        return user
    else:
        return None


#########################################################################################
#                                  AUTHENTICATION
#########################################################################################

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    clientid: Union[str, None] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

get_bearer_token = HTTPBearer(auto_error=False, scheme_name='Bearer token')


def verify_password(plain_password, hashed_password):
    return check_password_hash(hashed_password, plain_password)


def get_password_hash(password):
    return generate_password_hash(password, method='scrypt')


def authenticate_user(clientid: str, secret: str):
    user = find_user(clientid)
    if not user:
        return False
    if not verify_password(secret, user.secret):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    auth: t.Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(auth.credentials, API_SECRET_KEY, algorithms=[ALGORITHM])
        clientid: str = payload.get("sub")
        if clientid is None:
            raise credentials_exception
        token_data = TokenData(clientid=clientid)
    except JWTError:
        raise credentials_exception
    user = find_user(clientid=token_data.clientid)
    if user is None:
        raise credentials_exception
    return user
