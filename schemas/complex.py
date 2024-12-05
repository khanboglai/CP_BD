""" Описание модели комплекса """

from datetime import datetime
from pydantic import BaseModel


class ComplexModel(BaseModel):
    """ Модель комплекса """

    ISN: int
    name: str
    factory_id: int
    creation_date: datetime


class UpdateComplexModel(BaseModel):
    """ Модель для обновления """
    name: str
    factory_id: int
    creation_date: datetime
