""" Описание модели  компоненты """

from pydantic import BaseModel


class Component(BaseModel):
    """ Модель компоненты """

    # возможно добавлю id
    name: str
    count: int
    complex_name: str
