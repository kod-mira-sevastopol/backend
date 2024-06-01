import datetime
import random

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from AbstractModel import query_fetchone
from auth.models import User
from auth.schemas import UserCreate, UserRegistrationAccessPhone, UserAuthenticate
from exceptions import SuccessResponse
from jwt_handler import generate_jwt_token, create_refresh_token


async def get_user_by_email(db: AsyncSession, email: str):
    """
    Получить пользователя по почте. Возвращает Fasle если пользователя нет
    :param db:
    :param email:
    :return:
    """
    return await query_fetchone(db, select(User).where(User.email == email).limit(1), False)


async def get_user_by_phone(db: AsyncSession, phone: str):
    """
    Получить пользователя по телефону. Возвращает False если пользователя нет
    :param db:
    :param phone:
    :return:
    """
    return await query_fetchone(db, select(User).where(User.phone == phone).limit(1), False)


def random_number() -> int:
    """
    Генерирует рандомный код верификации
    :return:
    """
    return random.randint(100001, 999997)


def send_verification_email():
    """
    Имитируем отправку на почту
    :return:
    """
    code = random_number()
    return code


def send_verification_phone():
    """
    Имитируем отправку на телефон
    :return:
    """
    code = random_number()
    return code


async def setup_user(userdata: UserCreate) -> User:
    """
    Собирает юзера
    :param userdata:
    :return: User
    """
    if userdata.phone is not None:
        user = User(
            name=userdata.name,
            surname=userdata.surname,
            patronymic=userdata.patronymic,
            email=userdata.email,
            phone=userdata.phone,
            verification_code_phone=send_verification_phone()
        )
    else:
        user = User(
            name=userdata.name,
            surname=userdata.surname,
            patronymic=userdata.patronymic,
            email=userdata.email,
            phone=userdata.phone,
            verification_code_email=send_verification_email()
        )
    return user


async def addUser(db: AsyncSession, user: User):
    """
    Пытается сохранить юзера в БД
    :param db:
    :param user:
    :return:
    """
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        raise HTTPException(401, "Пользователь уже зарегистрирован. "
                                 "Введите код подтверждения или авторизуйтесь")


async def check_user_verify_phone(db: AsyncSession, phone):
    """
    Проверяет, что у пользователя не подтвержден ещё номер телефона
    :param db:
    :param userdata:
    :return: User
    """
    user = await get_user_by_phone(db, phone)
    if user is False:
        raise HTTPException(401, "Пользователь не зарегистрирован")
    if user.is_verified_phone:
        raise HTTPException(401, "Номер телефона подтвержден. Воспользуйтесь методами авторизации")
    return user


async def compare_code_phone(user: User, code: int):
    """
    Сравнивает код пользователя и код в БД
    :param user:
    :param code:
    :return:
    """
    if user.verification_code_phone != code:
        raise HTTPException(401, "Неверный код подтверждения")
    return user


async def clear_verification_phone_code(db: AsyncSession, user: User):
    """
    Убирает значение телефонного кода в NULL
    :param db:
    :param user:
    :return:
    """
    upd = await db.execute(update(User).where(User.phone == user.phone).values(verification_code_phone=None,
                                                                               is_verified_phone=True))
    await db.commit()
    return upd.rowcount


async def generate_tokens(db, user: User):
    """
    Возвращает словарь с двумя токенами и ролью
    :param db:
    :param user:
    :return:
    """
    data = {
        "id": user.id,
        "role": user.role
    }
    access_token = await generate_jwt_token(data, datetime.timedelta(days=365))
    refresh_token = await create_refresh_token(db, user.id, datetime.timedelta(days=365 * 2))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "role": user.role
    }


async def check_user_verify_email(db: AsyncSession, email: str):
    """
    Проверяет, что у пользователя не подтверждена почта
    :param db:
    :param userdata:
    :return: User
    """
    user = await get_user_by_email(db, email)
    if user is False:
        raise HTTPException(401, "Пользователь не зарегистрирован")
    if user.is_verified_email:
        raise HTTPException(401, "Email подтвержден. Воспользуйтесь методами авторизации")
    return user


async def compare_code_email(user: User, code: int):
    """
    Сравнивает код пользователя и код в БД
    :param user:
    :param code:
    :return:
    """
    if user.verification_code_email != code:
        raise HTTPException(401, "Неверный код подтверждения")
    return user


async def clear_verification_email_code(db: AsyncSession, user: User):
    """
    Убирает значение email кода в NULL
    :param db:
    :param user:
    :return:
    """
    upd = await db.execute(update(User).where(User.email == user.email).values(verification_code_email=None,
                                                                               is_verified_email=True))
    await db.commit()
    return upd.rowcount


async def get_authenticate_code_email(db: AsyncSession, email: str):
    """
    Процесс авторизации пользователя по почте
    :param db:
    :param email:
    :return:
    """
    user = await get_user_by_email(db, email)
    if user is False:
        raise HTTPException(404, "Пользователя не существует")
    if not user.is_verified_email:
        raise HTTPException(401, "E-mail не подтвержден")

    if user.verification_code_email is not None:
        raise HTTPException(401, "Код уже был отправлен")

    return await authenticate_email(db, email)


async def authenticate_email(db: AsyncSession, email: str):
    """
    Отправляет сообщение на почту и возвращает результат(для тестов - с кодом)
    :param db:
    :param email:
    :return:
    """
    code = send_verification_email()
    upd = await db.execute(
        update(User).where(User.email == email).values(verification_code_email=code))
    if upd.rowcount == 0:
        raise HTTPException(401, "Неизвестная ошибка")
    await db.commit()
    return SuccessResponse({"code": code})


async def get_authenticate_code_phone(db: AsyncSession, phone: str):
    """
    Процесс авторизации пользователя по телефону
    :param db:
    :param phone:
    :return:
    """
    user = await get_user_by_phone(db, phone)
    if user is False:
        raise HTTPException(401, "Пользователя не существует")

    if not user.is_verified_phone:
        raise HTTPException(401, "Телефон не подтвержден")

    if user.verification_code_phone is not None:
        raise HTTPException(401, "Код уже был отправлен")

    return await authenticate_phone(db, phone)


async def authenticate_phone(db: AsyncSession, phone: str):
    """
    Отправляет сообщение на телефон и возвращает результат(для тестов - с кодом)
    :param db:
    :param phone:
    :return:
    """
    code = send_verification_phone()
    upd = await db.execute(
        update(User).where(User.phone == phone).values(verification_code_phone=code))
    if upd.rowcount == 0:
        raise HTTPException(401, "Неизвестная ошибка")
    await db.commit()
    return SuccessResponse({"code": code})


async def authenticate_user_email(db: AsyncSession, data: UserAuthenticate):
    """
    Проверяем код пользователя и возвращаем токены
    :param db:
    :param data:
    :return:
    """
    user = await get_user_by_email(db, data.email)

    if user is False:
        raise HTTPException(404, "Пользователь не найден")

    if user.verification_code_email != data.code:
        raise HTTPException(401, "Неверный код")

    changed = await clear_verification_email_code(db, user)
    if changed == 0:
        raise HTTPException(404, "Неизвестная ошибка")
    await db.commit()
    return SuccessResponse({"info": await generate_tokens(db, user)})


async def authenticate_user_phone(db: AsyncSession, data: UserAuthenticate):
    """
        Проверяем код пользователя и возвращаем токены
        :param db:
        :param data:
        :return:
        """
    user = await get_user_by_phone(db, data.phone)

    if user is False:
        raise HTTPException(404, "Пользователь не найден")

    if user.is_verified_phone is False:
        raise HTTPException(401, "Пользователь не подтвердил регистрацию")

    if user.verification_code_phone != data.code:
        raise HTTPException(401, "Неверный код")

    changed = await clear_verification_phone_code(db, user)
    if changed == 0:
        raise HTTPException(404, "Неизвестная ошибка")
    await db.commit()
    return SuccessResponse({"info": await generate_tokens(db, user)})
