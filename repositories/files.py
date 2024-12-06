""" Функции для работы с таблицей файлов """

import logging
import asyncpg
from config import DATABASE_URL_ADM


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_files():
    """ получить все файлы из таблицы """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)

        query = """SELECT * FROM documents ORDER BY creation_date DESC"""

        rows = await conn.fetch(query)
        await conn.close()

        result = [dict(row) for row in rows]
        logger.info("Selected all files from documents")
        return result
    except ConnectionError as e:
        logger.error(e)
