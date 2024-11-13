""" Функции для работы с таблицей пользователей """

import logging
import asyncpg
from config import DATABASE_URL


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

        query = """SELECT * FROM storage"""

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
        return component_id

    except ConnectionError as e:
        logger.error(e)
