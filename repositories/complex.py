""" Функция для работы с таблицей комплексов """

import logging
import asyncpg
from config import DATABASE_URL


from schemas.complex import ComplexModel

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


async def get_complexes():
    """ Функция для выдачи комплексов """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM complexes"""
        rows = await conn.fetch(query)

        await conn.close()

        result = [dict(row) for row in rows]

        logger.info(f"Selected complexes data!")
        return result
    except asyncpg.PostgresError as e:
        logger.error(f"Error postgres {e}")


async def del_complex(id: int):
    """ Функция для удаления комплекса """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """DELETE FROM complexes WHERE ИСН=$1"""

        status = await conn.execute(query, id)
        await conn.close()

        logger.info(f"Deleted complex with id: {id}")
        return status
    except asyncpg.PostgresError as e:
        logger.error(e)


async def check_complex(id: int):
    """ Функция для проверки существования комплекса """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT ИСН FROM complexes WHERE ИСН=$1"""
        res = await conn.fetchval(query, id)

        await conn.close()
        logger.info("Checking complex success")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)


async def insert_complex_data(comlex: ComplexModel):
    """ Функция для вставки данных о комплексе """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """INSERT INTO complexes (ИСН, name, factory_id, creation_date)
        VALUES ($1, $2, $3, $4)
        RETURNING ИСН
        """

        res = await conn.fetchval(query, comlex.ISN, comlex.name, comlex.factory_id, comlex.creation_date)
        await conn.close()

        logger.info(f"Added new complex with id: {res}")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)
