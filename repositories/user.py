""" Функции для работы с таблицей пользователей """

import logging
import asyncpg
import bcrypt
from config import DATABASE_URL

from schemas.user import UpdateUserModel


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

        query = """SELECT *, DATE_PART('year', AGE(current_date, birth_date))::INTEGER AS age FROM users"""

        rows = await conn.fetch(query)
        result = [dict(row) for row in rows]
        await conn.close()

        logger.info("Selected all users")
        return result

    except ConnectionError as e:
        logger.error(e)


async def get_user(login: str):
    """ Функция возвращает пользователя """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """SELECT *, DATE_PART('year', AGE(current_date, birth_date))::INTEGER AS age FROM users WHERE login=$1"""

        row = await conn.fetchrow(query, login)
        await conn.close()

        logger.info(f"Selected user with login {login}")
        return row

    except ConnectionError as e:
        logger.error(e)


async def delete_user(login: str):
    """ Функция возвращает пользователя """

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """DELETE FROM users WHERE login=$1"""

        status = await conn.execute(query, login)
        await conn.close()

        logger.info(f"Deleted user with login {login}")
        return status

    except asyncpg.PostgresError as e:
        logger.error(e)


async def update_usr(id: int, user_data: UpdateUserModel):
    """ Функция для обновления данных пользователя """

    try:
        conn = await asyncpg.connect(DATABASE_URL)
        query = """UPDATE users
        SET name=$2, surname=$3, birth_date=$4, email=$5, login=$6, hashed_password=$7
        WHERE id=$1
        RETURNING id
        """

        res = await conn.fetchval(query, id, 
                                user_data.name, 
                                user_data.surname, 
                                user_data.birth_date, 
                                user_data.email,
                                user_data.login,
                                user_data.hashed_password)
        
        await conn.close()

        logger.info(f"Updated user with id: {id}")
        return res
    except asyncpg.PostgresError as e:
        logger.error(e)
