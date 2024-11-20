""" Описание модели блока """

from pydantic import BaseModel


class DetailModel(BaseModel):
    """ Модель блока/детали """

    name: str
    count: int
    complex_name: str    
