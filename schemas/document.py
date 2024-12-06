""" Описание модели отчета """

from datetime import datetime
from pydantic import BaseModel


class Document(BaseModel):
    """ Модель отчета """

    name: str
    creation_date: datetime
    file_path: str
    author_login: str
