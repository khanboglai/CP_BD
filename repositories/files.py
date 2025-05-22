""" Функции для работы с таблицей файлов """
import json

import asyncpg
from config import DATABASE_URL_ADM, logger, default_serializer
from redis_session import redis_client


FILE_CACHE_KEY = "cached_file_data"
FILE_CACHE_TTL = 600


async def get_cached_files():
    """ Получение кеша файлов """
    cached = await redis_client.get(FILE_CACHE_KEY)
    if cached:
        logger.info("Get cached files data")
        return json.loads(cached)


async def set_cached_files(file_data):
    await redis_client.setex(FILE_CACHE_KEY, FILE_CACHE_TTL, json.dumps(file_data, default=default_serializer))
    logger.info("Set cached files data")


async def clear_cached_files():
    await redis_client.delete(FILE_CACHE_KEY)
    logger.info("Clear cached files data")


async def get_files():
    """ получить все файлы из таблицы """

    cached = await get_cached_files()
    if cached:
        logger.info("Get cached files data")
        return json.loads(cached)

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)

        query = """SELECT * FROM documents ORDER BY creation_date DESC"""

        rows = await conn.fetch(query)
        await conn.close()

        result = [dict(row) for row in rows]
        logger.info("Selected all files from documents")
        await set_cached_files(result)
        return result
    except ConnectionError as e:
        logger.error(e)
