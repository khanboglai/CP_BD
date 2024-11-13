""" Описание модели пользователя """

from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr


class UserModel(BaseModel):

    """ Класс пользователя системы """

    name: str
    surname: str
    birth_date: datetime
    age: int
    email: EmailStr
    login: str
    hashed_password: str

    '''
        Валидация не обязательна, но желатьельна, для системного адина.
        Валидация происходит на фронте
    '''

    @field_validator('age')
    def check_age(cls, value):
        """ Проверка на возраст """
        if value < 0:
            raise ValueError("Age must be more than 0")
        return value
