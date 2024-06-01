from sqlalchemy import Column, String, Boolean, Integer, ForeignKey

from src.AbstractModel import AbstractModel


class User(AbstractModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True, index=True)
    phone = Column(String, nullable=False, unique=True, index=True)
    is_verified_phone = Column(Boolean, server_default="false")
    is_verified_email = Column(Boolean, server_default="false")
    verification_code_phone = Column(Integer)
    verification_code_email = Column(Integer)
    role = Column(String, default="user")


class Score(AbstractModel):
    __tablename__ = "scores"

    user_id = Column(Integer, ForeignKey("users.id"))
    operation = Column(Integer, default=0, nullable=False)
    count = Column(Integer, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"))


class Config(AbstractModel):
    __tablename__ = 'config'
    __table_args__ = {'extend_existing': True}

    expires_at = Column(Integer)
    expires_in = Column(Integer)
    access_token = Column(String)
