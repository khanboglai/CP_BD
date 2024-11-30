""" Описание модели отчета """

from datetime import datetime
from pydantic import BaseModel, validator


class Document(BaseModel):
    """ Модель отчета """

    name: str
    creation_date: datetime
    file_path: str
    author_id: int
