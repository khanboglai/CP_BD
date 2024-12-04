""" Функция для работы с таблицей комплексов """

import logging
import asyncpg
from config import DATABASE_URL


# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_complex(complex_id: int):
    """ Функция для выдачи комплекса """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM complexes WHERE ИСН=$1"""
        row = await conn.fetchrow(query, complex_id)

        await conn.close()
        logger.info(f"Selected complex data for row: {row['ИСН']}")
        return row

    except asyncpg.PostgresError as e:
        logger.error(f"Error postgres {e}")