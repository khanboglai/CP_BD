""" Описание модели отчета """

from datetime import datetime
from pydantic import BaseModel, validator


class Document(BaseModel):
    """ Модель отчета """

    name: str
    creation_date: datetime
    author_id: int
