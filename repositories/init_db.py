import asyncpg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db(database_url):
    # Подключение к базе данных
    try:
        conn = await asyncpg.connect(database_url)
        
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
        logger.info("Connect to BD done")
    except Exception as e:
        logger.error(e)
