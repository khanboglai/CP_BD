""" Функции для работы с таблицей аналитики """

import logging
import asyncpg
from config import DATABASE_URL_ADM


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_analitic():
    """ получить все записи """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)

        query = """SELECT * FROM analitic_view"""

        rows = await conn.fetch(query)
        await conn.close()

        result = [dict(row) for row in rows]
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

        logger.info("Deleted all row from user_activity_log")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)
