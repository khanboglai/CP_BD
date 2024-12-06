""" Функция для работы с таблицей комплексов """

import logging
import asyncpg
from config import DATABASE_URL_ADM


# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_data():
    """ Функция для выдачи всех записей """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
        query = """SELECT * FROM works"""

        rows = await conn.fetch(query)
        await conn.close()

        res = [dict(row) for row in rows]

        logger.info("Selected all rows in table works")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)


async def insert_row(data: dict):
    """ Функция для вставки данных """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
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
        await conn.close()

        logger.info(f"Inserted row with id {work_id}")
        return work_id
    except asyncpg.PostgresError as e:
        logger.error(e)
