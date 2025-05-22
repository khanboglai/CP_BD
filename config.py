""" Тут лежат ссылки для всего приложения """
import logging
import os
from datetime import datetime

# DB
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ADM = os.getenv("DATABASE_URL_ADM") 

REDIS_HOST: str = "redis"
REDIS_PORT: int = 6379
REDIS_SESSION_DB: int = 1
SESSION_SECRET_KEY: str = "your-secret-key-here"
SESSION_TTL: int = 3600  # 1 час в секундах

# логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# кастомный сериализатор для даты
def default_serializer(obj):
    """ Сериализатор для даты """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")