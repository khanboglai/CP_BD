""" Функция для работы с таблицей комплексов """

import logging
import asyncpg
from config import DATABASE_URL_ADM


from schemas.complex import ComplexModel, UpdateComplexModel

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_complex(complex_id: int):
    """ Функция для выдачи комплекса """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)

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
        conn = await asyncpg.connect(DATABASE_URL_ADM)

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
        conn = await asyncpg.connect(DATABASE_URL_ADM)

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
        conn = await asyncpg.connect(DATABASE_URL_ADM)

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
        conn = await asyncpg.connect(DATABASE_URL_ADM)

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


async def update_row(id: int, data: UpdateComplexModel):
    """ Функция для обновления пользователя """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
        query = """UPDATE complexes
        SET name=$2, factory_id=$3, creation_date=$4
        WHERE ИСН=$1
        RETURNING ИСН"""

        complex_id = await conn.fetchval(query, id, data.name, data.factory_id, data.creation_date)
        await conn.close()

        logger.info(f"Updated row with id: {complex_id}")
        return complex_id

    except asyncpg.PostgresError as e:
        logger.error(e)
