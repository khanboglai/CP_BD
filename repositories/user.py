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

        query = """INSERT INTO users (name, surname, birth_date, email, login, hashed_password, usr_role)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """

        values = (
            user_data['name'],
            user_data['surname'],
            user_data['birth_date'],
            user_data['email'],
            user_data['login'],
            hash_password(user_data['hashed_password']),
            user_data['user_role']
        )

        user_id = await conn.fetchval(query, *values)
        await conn.close()

        if user_id:
            logger.info("insert query done for user %s", user_data['login'])
            return user_id
        logger.error(f"User with login {user_data['login']} already exist!")
        return None
    except ConnectionError as e:
        logger.error(e)


async def auth_user(login: str, password: str):

    """ проверка данных пользователя """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT id, usr_role, hashed_password FROM users WHERE login = $1"""
        res = await conn.fetchrow(query, login)

        await conn.close()

        if res is None: # если пользователя нет
            return False

        if bcrypt.checkpw(password.encode('utf-8'), res['hashed_password'].encode('utf-8')):
            logger.info("auth %s complete", login)
            return res  # Успешная аутентификация
        return False  # Неверный пароль

    except ConnectionError as e:
        logger.error(e)


async def get_users():
    """ Функция возвращает всех пользователей """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT * FROM users"""

        rows = await conn.fetch(query)
        result = [dict(row) for row in rows]
        await conn.close()

        logger.info("Selected all users")
        return result

    except ConnectionError as e:
        logger.error(e)
