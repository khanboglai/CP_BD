""" Функции для работы с таблицей заявок """
import json
import asyncpg
from config import DATABASE_URL, logger


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
        RETURNING id, ИСН, problem, date
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


async def get_details(complex_name: str):
    """ Фукнция для выдачи делалей для комплекса """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM storage WHERE complex_name = $1"""

        rows = await conn.fetch(query, complex_name)
        result = [dict(row) for row in rows]
        await conn.close()

        return result

    except ConnectionError as e:
        logger.error(e)


async def cancel_update(id: int):
    """ Функция для обновления статуса и выдачи строки из таблицы """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """UPDATE trouble_tickets
        SET status=false
        WHERE id = $1
        RETURNING id
        """
    
        row = await conn.fetchrow(query, id)

        await conn.close()

        logger.info("Cancel updating")
        return row
    except ConnectionError as e:
        logger.error(e)