from pydantic import BaseModel


class EditSelfScore(BaseModel):
    count: int


class EditScore(EditSelfScore):
    user_id: int


class EditUserName(BaseModel):
    name: str


class EditUserSurname(BaseModel):
    surname: str


class EditUserPatronymic(BaseModel):
    patronymic: str