""" Функции для работы с таблицей пользователей """

import logging
import asyncpg
import bcrypt
from config import DATABASE_URL


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str):

    """ генерация соли и хеширование пароля """

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def insert_user(user_data: dict):

    """ вставка пользователя в базу данных """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """INSERT INTO users (name, surname, birth_date, age, email, login, hashed_password)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """

        values = (
            user_data['name'],
            user_data['surname'],
            user_data['birth_date'],
            user_data['age'],
            user_data['email'],
            user_data['login'],
            hash_password(user_data['hashed_password'])
        )

        user_id = await conn.fetchval(query, *values)
        await conn.close()

        logger.info("insert query done for user %s", user_data['login'])
        return user_id
    except ConnectionError as e:
        logger.error(e)


async def auth_user(login: str, password: str):

    """ проверка данных пользователя """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT hashed_password FROM users WHERE login = $1"""
        res = await conn.fetchrow(query, login)

        await conn.close()

        if res is None:
            raise AttributeError("Login don't exist")

        if bcrypt.checkpw(password.encode('utf-8'), res['hashed_password'].encode('utf-8')):
            logger.info("auth %s complete", login)
            return True  # Успешная аутентификация
        return False  # Неверный пароль

    except ConnectionError as e:
        logger.error(e)
