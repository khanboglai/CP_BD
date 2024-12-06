import logging
import asyncpg
import asyncio
import json
import bcrypt
from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr


class UserModel(BaseModel):
    """ Класс пользователя системы """

    name: str
    surname: str
    birth_date: datetime
    email: EmailStr
    login: str
    hashed_password: str
    user_role: str


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str):

    """ генерация соли и хеширование пароля """

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def insert_data(user: UserModel):
    try:
        conn = await asyncpg.connect("postgresql://admin1:admin@localhost:5432/service_center")

        query = """INSERT INTO users (name, surname, birth_date, email, login, hashed_password, usr_role)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """

        values = (user.name, user.surname, user.birth_date, user.email, user.login, hash_password(user.hashed_password), user.user_role)
        user_id = await conn.fetchval(query, *values)
        await conn.close()

        if user_id:
            logger.info("Insert query done for user %s", user.login)
            return user_id
        logger.error(f"User with login {user.login} already exists!")
        return None
    except asyncpg.PostgresError as e:
        logger.error(e)

async def load_users_from_json(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        users_data = json.load(file)
        for user_data in users_data:
            user = UserModel(
                name=user_data['name'],
                surname=user_data['surname'],
                birth_date = datetime.fromisoformat(user_data['birth_date']),
                email=user_data['email'],
                login=user_data['login'],
                hashed_password=user_data['hashed_password'],
                user_role=user_data['usr_role']
            )
            await insert_data(user)


async def main(file_name):
    await load_users_from_json(file_name)

if __name__ == "__main__":
    asyncio.run(main("repositories/admin.json"))
