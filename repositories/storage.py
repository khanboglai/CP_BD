""" Функции для работы с таблицей пользователей """

import logging
import asyncpg
from config import DATABASE_URL, DATABASE_URL_ADM


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def insert_data(storage_data: dict):
    """ вставка коплектующих в таблицу склада """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """INSERT INTO storage (name, count, complex_name)
        VALUES ($1, $2, $3)
        RETURNING id
        """

        values = (
            storage_data['name'],
            storage_data['count'],
            storage_data['complex_name']
        )

        component_id = await conn.fetchval(query, *values)
        await conn.close()

        logger.info("insert query done for component %s", storage_data['name'])
        return component_id

    except ConnectionError as e:
        logger.error(e)


async def get_data():
    """ Выдает данные для отображения """
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM storage ORDER BY complex_name"""

        rows = await conn.fetch(query)
        result = [dict(row) for row in rows]
        await conn.close()

        
        return result

    except ConnectionError as e:
        logger.error(e)


async def update_data(id: int, count: int):
    """ Функция для обновления данных """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """UPDATE storage
        SET count = $2
        WHERE id = $1
        RETURNING id
        """

        values = (
            id,
            count
        )

        component_id = await conn.fetchval(query, *values)

        await conn.close()
        logger.info(f"Details for {component_id} updated!")
        return component_id

    except ConnectionError as e:
        logger.error(e)


async def delete_data(id: int):
    """ Функция для удаления записи из таблицы склада """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
        query = """DELETE FROM storage WHERE id=$1"""

        res = await conn.execute(query, id)
        await conn.close()

        logger.info(f"Deleted detail: {id} from storage")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)


async def get_row(complex_name: str):
    """ Функция для выдачи строки """

    try:
        conn  = await asyncpg.connect(DATABASE_URL)
        query = """SELECT * FROM storage WHERE complex_name=$1"""

        res = await conn.fetchrow(query, complex_name)

        await conn.close()

        return res
    except asyncpg.PostgresError as e:
        logger.error(e)


async def get_detail_name(conn, id: int):
    """ Функция для выдачи имени детали и обновления колличества """

    try:
        # conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT name FROM storage WHERE id=$1"""
        complex_name = await conn.fetchval(query, id)

        return complex_name
    except ConnectionError as e:
        logger.error(e)


async def insert_used_detalis(conn, work_id: int, detail_id: int):
    """ Функция для вставки деталей в промежуточную таблицу """

    try:
        # conn = await asyncpg.connect(DATABASE_URL)
        query = """INSERT INTO used_details (work_id, detail_id)
        VALUES ($1, $2)
        RETURNING id
        """

        row_id = await conn.fetchval(query, work_id, detail_id)

        logger.info(f"Inserted data in table used_datails with id: {row_id}")
        return row_id
    except asyncpg.PostgresError as e:
        logger.error(e)
