import datetime
import os
import time
from typing import Optional

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

#from AbstractModel import query_fetchone

#from auth.router import security

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()


async def generate_jwt_token(payload: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Генерирует access_token
    :param payload:
    :param expires_delta:
    :return:
    """
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
        payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    """
    Декодирует jwt_token любой
    :param token:
    :return:
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен просрочен")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")


async def verify_jwt_token(token):
    token = token.credentials
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        expiration_time = decoded_token.get("exp")
        if "role" not in decoded_token.keys():
            raise HTTPException(401, "Передан не access_token")
        if expiration_time:
            current_time = datetime.datetime.utcnow()
            if current_time < datetime.datetime.fromtimestamp(expiration_time):
                return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Срок действия токена истёк. Обрaтитесь за новым токеном")
    except jwt.JWTError:
        raise HTTPException(401, "Неверный токен")

    raise HTTPException(401, "Токен недействителен")


async def verify_token_and_check_role_user(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль юзера
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    role = decoded_token['role']
    if role != "user":
        raise HTTPException(403, "У вас нет доступа.")
    return decoded_token


async def verify_token_and_check_role_admin(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль админа
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    role = decoded_token['role']
    if role != "admin":
        raise HTTPException(403, "У вас нет доступа.")
    return decoded_token


async def verify_token_and_check_role_all(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль юзера
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    return decoded_token


async def verify_token_and_check_role_recruiter(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль рекрутера
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    role = decoded_token['role']
    if role != "recruiter":
        raise HTTPException(403, "У вас нет доступа.")
    return decoded_token


async def verify_token_and_check_role_hiring_manager(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль нанимающего менеджера
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    role = decoded_token['role']
    if role != "hiring_manager":
        raise HTTPException(403, "У вас нет доступа.")
    return decoded_token


async def verify_token_and_check_role_hiring_manager_and_recruiter(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль нанимающего менеджера или рекрутера
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    role = decoded_token['role']
    if role not in ("hiring_manager", "recruiter"):
        raise HTTPException(403, "У вас нет доступа.")
    return decoded_token


async def verify_token_and_check_role_hiring_manager_and_resource_manager(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверяет роль нанимающего менеджера или рекрутера
    :param token:
    :return:
    """
    decoded_token = await verify_jwt_token(token)
    role = decoded_token['role']
    if role not in ("hiring_manager", "resource_manager"):
        raise HTTPException(403, "У вас нет доступа.")
    return decoded_token