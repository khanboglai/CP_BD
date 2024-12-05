""" Описание модели пользователя """

from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr


class UserModel(BaseModel):
    """ Класс пользователя системы """

    name: str
    surname: str
    birth_date: datetime
    email: EmailStr
    login: str
    hashed_password: str
    user_role: str


class UpdateUserModel(BaseModel):
    """ Схема для обновления данных """

    name: str
    surname: str
    birth_date: datetime
    email: EmailStr
    login: str
    hashed_password: str
