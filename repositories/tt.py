""" Функции для работы с таблицей заявок """

import logging
import asyncpg
from config import DATABASE_URL


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_data():
    """ Функция для выдачи строк из таблицы """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM trouble_tickets WHERE status=false"""

        rows = await conn.fetch(query)
        result = [dict(row) for row in rows]
        await conn.close()

        return result
    except ConnectionError as e:
        logger.error(e)


async def update_get_row(id: int):
    """ Функция для обновления статуса и выдачи строки из таблицы """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """UPDATE trouble_tickets
        SET status=true
        WHERE id = $1
        RETURNING id, name, problem, date
        """
    
        row = await conn.fetchrow(query, id)

        # tt = [dict(elem) for elem in row]
        await conn.close()

        return row
    except ConnectionError as e:
        logger.error(e)


async def get_row(id: int):
    """ Функция для выдачи строки """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM trouble_tickets WHERE id = $1"""

        row = await conn.fetchrow(query, id)

        await conn.close()

        return row
    except ConnectionError as e:
        logger.error(e)
