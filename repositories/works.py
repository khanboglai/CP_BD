""" Функция для работы с таблицей комплексов """
import json

import asyncpg
from config import DATABASE_URL_ADM, logger, default_serializer
from redis_session import redis_client


WORK_CACHE_KEY = "cached_works_data"
WORK_CACHE_TTL = 600


async def get_works_data():
    """ Получаем данные по работам из redis """
    cached = await redis_client.get(WORK_CACHE_KEY)
    if cached:
        logger.info("Get cached works data")
        return json.loads(cached)
    return None


async def set_cached_works_data(works_data):
    """ Загружаем данные в redis """
    await redis_client.setex(WORK_CACHE_KEY, WORK_CACHE_TTL, json.dumps(works_data, default=default_serializer))
    logger.info("Set cached works data")


async def clear_works_cache():
    """ Очищаем кэш, это нужно для обновления """
    await redis_client.delete(WORK_CACHE_KEY)
    logger.info("Clear cached works data")


async def get_data():
    """ Функция для выдачи всех записей """

    cached_data = await get_works_data()
    if cached_data:
        return cached_data


    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
        query = """SELECT * FROM works"""

        rows = await conn.fetch(query)
        await conn.close()

        res = [dict(row) for row in rows]

        logger.info("Selected all rows in table works")
        await set_cached_works_data(res)
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)


async def insert_row(conn, data: dict):
    """ Функция для вставки данных """

    try:
        # conn = await asyncpg.connect(DATABASE_URL_ADM)
        query = """INSERT INTO works (worker_login, ИСН, finisd_date, description, tt_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """

        values = (
            data["worker_login"],
            data["ИСН"],
            data["finisd_date"],
            data["description"],
            data["tt_id"]
        )

        work_id = await conn.fetchval(query, *values)
        # await conn.close()

        logger.info(f"Inserted row with id {work_id}")
        return work_id
    except asyncpg.PostgresError as e:
        logger.error(e)
