from sqlalchemy import Column, Boolean, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from AbstractModel import AbstractModel


class User(AbstractModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True, index=True)
    phone = Column(String, nullable=True, unique=True, index=True)
    is_verified_phone = Column(Boolean, server_default="false")
    is_verified_email = Column(Boolean, server_default="false")
    verification_code_phone = Column(Integer)
    verification_code_email = Column(Integer)
    role = Column(String, default="user")
    photo = Column(String)

    tokens = relationship("RefreshToken", backref="user")


class RefreshToken(AbstractModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(Integer)


class Contact(AbstractModel):
    __tablename__ = "contacts"

    tg_id = Column(String, index=True, unique=True)
    vk_id = Column(String, unique=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)





