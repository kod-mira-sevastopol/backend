from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from jwt_handler import verify_jwt_token, verify_token_and_check_role_user, verify_refresh_token
from .service import *

registration_router = APIRouter(prefix="/create", tags=["Registration"])
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()


@registration_router.post("/", summary="Создаёт пользователя, отправляет код подтверждения на почту/телефон")
async def user_create(user: UserCreate, db=Depends(get_session)):
    return await create_user(db, user)


@registration_router.post("/verify_by_phone", summary="Верифицирует номер телефона пользователя")
async def verify_by_phone(user: UserRegistrationAccessPhone, db=Depends(get_session)):
    return await verify_user_by_phone(db, user)


@registration_router.post("/verify_by_email", summary="Верифицирует email пользователя")
async def verify_by_email(user: UserRegistrationAccessEmail, db=Depends(get_session)):
    return await verify_user_by_email(db, user)


@auth_router.post("/get_code", summary="Получить код авторизации")
async def auth_get_code(user: UserAuthenticationGetCode, db=Depends(get_session)):
    return await get_authenticate_code(db, user)


@auth_router.post("/authenticate", summary="Отправить код авторизации")
async def auth_authenticate(user: UserAuthenticate, db=Depends(get_session)):
    return await authenticate_user(db, user)


@auth_router.post("/refresh", summary="Поменять токен")
async def refresh_access_token(request: Request,
                               token_data: HTTPAuthorizationCredentials = Depends(verify_refresh_token),
                               db=Depends(get_session)):
    token = request.headers['authorization'].split()[1]
    return await refresh_token(db, token, token_data)



@auth_router.post("/registration_with_telegram")
async def authorization_with_telegram(data: AuthorizationTelegram,
                                     db=Depends(get_session)):
    return await authorizationWithTelegram(db, data)


