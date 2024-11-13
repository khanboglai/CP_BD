""" Описание модели для заявок на ремонт """

from datetime import datetime
from pydantic import BaseModel


class TTModel(BaseModel):
    """ Модель для заявок на ремонт """

    name: str
    date: datetime
    problem: str
    status: bool
