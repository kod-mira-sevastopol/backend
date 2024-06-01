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

from AbstractModel import query_fetchone
from auth.models import RefreshToken, User

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


def generate_refresh_token(user_id: int, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Генерирует refresh-токен
    :param user_id:
    :param expires_delta:
    :return:
    """
    payload = {"user_id": user_id}
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
        payload.update({"exp": expire})
    encoded_refresh_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


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


async def create_refresh_token(db: AsyncSession, user_id: int,
                               expires_delta: Optional[datetime.timedelta] = None) -> RefreshToken:
    """
    Создает рефреш токен, добавляет его в БД
    :param db:
    :param user_id:
    :param expires_delta:
    :return:
    """
    expires_at = datetime.datetime.utcnow() + expires_delta
    expires_at_timestamp = int(time.mktime(expires_at.timetuple()))

    refresh_token = RefreshToken(
        user_id=user_id,
        token=generate_refresh_token(user_id, expires_delta),
        expires_at=expires_at_timestamp
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def get_refresh_token(db: AsyncSession, token: str) -> RefreshToken:
    """
    Получает refresh-токен БД
    :param db:
    :param token:
    :return:
    """
    query = select(RefreshToken).where(RefreshToken.token == token)
    result = await db.execute(query)
    refresh_token = result.fetchone()
    if refresh_token:
        return refresh_token[0]
    else:
        raise HTTPException(401, "Ошибка передачи refresh-токена")


async def revoke_refresh_token(db: AsyncSession, refresh_token: RefreshToken):
    """
    Удаляет refresh-токен из БД
    :param db:
    :param refresh_token:
    :return:
    """
    query = delete(RefreshToken).where(RefreshToken.id == refresh_token.id)
    await db.execute(query)
    await db.commit()


async def refresh_jwt_token(db: AsyncSession, refresh_token: RefreshToken) -> str:
    """

    :param db:
    :param refresh_token:
    :return:
    """
    current_time = int(time.mktime(datetime.datetime.utcnow().timetuple()))

    if refresh_token.expires_at < current_time:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh-токен просрочился")
    user_id = refresh_token.user_id
    user = await query_fetchone(db, select(User).where(User.id == user_id).limit(1))
    new_jwt_token = await generate_jwt_token({"id": user_id, "role": user.role}, datetime.timedelta(days=365))
    await revoke_refresh_token(db, refresh_token)
    return new_jwt_token


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
        raise HTTPException(401,"Срок действия токена истёк. Обрaтитесь за новым токеном")
    except jwt.JWTError:
        raise HTTPException(401, "Неверный токен")

    raise HTTPException(401, "Токен недействителен")


async def verify_refresh_token(token: HTTPAuthorizationCredentials = Depends(security)):
    token = token.credentials
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        expiration_time = decoded_token.get("exp")
        if "role" in decoded_token.keys():
            raise HTTPException(401, "Передан не refresh-token")
        if expiration_time:
            current_time = datetime.datetime.utcnow()
            if current_time < datetime.datetime.fromtimestamp(expiration_time):
                return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(401,"Срок действия токена истёк. Обрaтитесь за новым токеном")
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
