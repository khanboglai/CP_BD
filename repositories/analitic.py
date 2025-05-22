""" Функции для работы с таблицей аналитики """
import json

import asyncpg
from config import DATABASE_URL_ADM, logger
from redis_session import redis_client


ANALITYC_CACHE_KEY = "cached_analytic_data"
CACHE_TTL = 300 # 5 mins


async def get_cached_analytic():
    """ Функция для получения аналитики из БД """
    cached = await redis_client.get(ANALITYC_CACHE_KEY)
    if cached:
        logger.info("Get cached analytic")
        return json.loads(cached)
    return None


async def set_cached_analytic(data):
    """ Сохранить аналитику в redis """
    await redis_client.setex(ANALITYC_CACHE_KEY, CACHE_TTL, json.dumps(data))
    logger.info("Set cached analytic")


async def clear_analytic_cache():
    """ Очищение аналитики """
    await redis_client.delete(ANALITYC_CACHE_KEY)
    logger.info("Кэш аналитики очищен")


async def get_analitic():
    """ получить все записи """

    cached_data = await get_cached_analytic()
    if cached_data:
        return cached_data

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)

        query = """SELECT * FROM analitic_view"""

        rows = await conn.fetch(query)
        await conn.close()

        result = [dict(row) for row in rows]

        await set_cached_analytic(result)
        logger.info("Selected all files from user_activity_log")
        return result
    except ConnectionError as e:
        logger.error(e)


async def delete_analitic():
    """ Функция для очистки таблицы статистики """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
        query = """DELETE FROM user_activity_log"""

        res = await conn.execute(query)
        await conn.close()

        await clear_analytic_cache()
        logger.info("Delete cached analytic")

        logger.info("Deleted all row from user_activity_log")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)
