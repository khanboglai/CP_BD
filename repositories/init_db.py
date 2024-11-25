""" Скрипт инициализации базы данных """

import logging
import asyncpg

from config import DATABASE_URL


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_table_users():
    """ создание таблицы пользователей """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # Создание таблицы пользователей, если она не существует
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            surname VARCHAR(100),
            birth_date TIMESTAMP,
            age INT CHECK (age >= 0),
            email VARCHAR(100) UNIQUE,
            login VARCHAR(100) UNIQUE,
            hashed_password VARCHAR(100)
            )
        ''')

        await conn.close()
        logger.info("Created table: users")
    except ConnectionError as e:
        logger.error(e)


async def create_table_storage():
    """ создане таблицы для склада """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS storage (
            id SERIAL PRIMARY KEY,
            name VARCHAR(300),
            count INT,
            complex_name VARCHAR(200)
            )
        ''')

        await conn.close()
        logger.info("Created table: storage")
    except ConnectionError as e:
        logger.error(e)


async def create_table_tt():
    """ создание таблицы заявок """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS trouble_tickets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(300),
            problem VARCHAR(1000),
            date TIMESTAMP,
            status BOOLEAN
            )
        ''')

        await conn.close()

        logger.info("Created table: trouble_tickets ")

    except ConnectionError as e:
        logger.error(e)


async def create_table_document():
    """ Создание таблицы для докментов """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            name VARCHAR(300),
            creation_date TIMESTAMP,
            author_id INT,
            FOREIGN KEY (author_id) REFERENCES users(id)
            )
        ''')

        await conn.close()
        
        logger.info("Created table: documents ")

    except ConnectionError as e:
        logger.error(e)


async def init_db():

    """ создание таблиц в базе данных """

    await create_table_users()
    await create_table_storage()
    await create_table_tt()
    await create_table_document()
