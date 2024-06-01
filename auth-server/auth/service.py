import os

from psycopg2 import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from AbstractModel import query_fetchone
from exceptions import SuccessResponse
from jwt_handler import decode_jwt_token, refresh_jwt_token
from .models import RefreshToken, Contact, User
from .schemas import *
from .utils import setup_user, addUser, check_user_verify_phone, clear_verification_phone_code, \
    generate_tokens, compare_code_phone, check_user_verify_email, compare_code_email, clear_verification_email_code, \
    get_authenticate_code_email, get_authenticate_code_phone, authenticate_user_email, authenticate_user_phone


async def create_user(db: AsyncSession, user: UserCreate):
    """
    Создаёт пользователя
    :param db:
    :param user:
    :return:
    """
    user = await setup_user(user)
    user = await addUser(db, user)
    return SuccessResponse({"user": await user.to_dict()}, 201)


async def verify_user_by_phone(db: AsyncSession, userdata: UserRegistrationAccessPhone):
    """
    Верифицирует пользователя по номеру телефона
    :param db:
    :param userdata:
    :return:
    """
    user = await check_user_verify_phone(db, userdata.phone)
    user = await compare_code_phone(user, userdata.code)
    changed = await clear_verification_phone_code(db, user)
    if changed == 0:
        raise HTTPException(401, "Неверные данные")
    return SuccessResponse({"data": await generate_tokens(db, user)})


async def verify_user_by_email(db: AsyncSession, userdata: UserRegistrationAccessEmail):
    """
    Верифицирует пользователя по email
    :param db:
    :param userdata:
    :return:
    """
    user = await check_user_verify_email(db, userdata.email)
    user = await compare_code_email(user, userdata.code)
    changed = await clear_verification_email_code(db, user)
    if changed == 0:
        raise HTTPException(401, "Неверные данные")
    return SuccessResponse({"data": await generate_tokens(db, user)})


async def get_authenticate_code(db: AsyncSession, data: UserAuthenticationGetCode):
    """
    Отправляет код аутентификации по переданному параметру [email, phone]
    :param db:
    :param data:
    :return:
    """
    if data.email is not None:
        return await get_authenticate_code_email(db, data.email)
    else:
        return await get_authenticate_code_phone(db, data.phone)


async def authenticate_user(db: AsyncSession, data: UserAuthenticate):
    """
    Проверяет код подтверждения
    :param db:
    :param data:
    :return:
    """
    if data.email is not None:
        return await authenticate_user_email(db, data)
    else:
        return await authenticate_user_phone(db, data)


async def refresh_token(db: AsyncSession, token: str, token_data: dict):
    """
    Отдает новый access_токен по рефрешу
    :param db:
    :param token:
    :param token_data:
    :return:
    """
    refresh_token = RefreshToken(user_id=token_data['user_id'], token=token, expires_at=token_data['exp'])
    new_token = await refresh_jwt_token(db, refresh_token)
    return SuccessResponse({
        "access_token": new_token
    })


async def authorizationWithTelegram(db: AsyncSession, data: AuthorizationTelegram):
    """
    Создает пользователя и привязывает его к телеге
    :param db:
    :param data:
    :return:
    """

    original_key = os.getenv("secret_service_key")
    if original_key != data.secret_service_key:
        raise HTTPException(401, "Неверный secret_service_key")

    user = await query_fetchone(db, select(Contact).where(Contact.tg_id == data.telegram_id).limit(1), False)

    if user:
        new_user = await query_fetchone(db, select(User).where(User.id == user.user_id).limit(1))
        return SuccessResponse({"data": await generate_tokens(db, new_user)})

    create_user = User(name="Имя", surname="Фамилия", patronymic="Отчество", phone="Auth by TG")
    db.add(create_user)
    try:
        await db.commit()
        await db.refresh(create_user)
        new_contact = Contact(tg_id=data.telegram_id, user_id=create_user.id)
        db.add(new_contact)
        await db.commit()
        await db.refresh(new_contact)
        return SuccessResponse({"data": await generate_tokens(db, create_user)})
    except IntegrityError:
        raise HTTPException(403, "Данные повторяются")



