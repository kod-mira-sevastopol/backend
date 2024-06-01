from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic.v1 import validator


class UserBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

    @validator('*', pre=True)
    def check_fields(cls, value, values, **kwargs):
        if 'email' in values and 'phone' in values and values['email'] is None and values['phone'] is None:
            raise HTTPException(401, 'email или phone не может быть пустым')
        return value


class UserCreate(UserBase):
    name: str
    surname: str
    patronymic: Optional[str] = None


class UserAuthenticationGetCode(UserBase):
    pass


class UserAuthenticate(UserBase):
    code: int


class UserRegistrationAccess(BaseModel):
    code: int


class UserRegistrationAccessEmail(UserRegistrationAccess):
    email: str


class UserRegistrationAccessPhone(UserRegistrationAccess):
    phone: str


class AuthorizationTelegram(BaseModel):
    telegram_id: str
    secret_service_key: str



