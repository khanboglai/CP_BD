import asyncpg
import json
import logging
from config import DATABASE_URL_ADM
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serialize_row(row):
    """Преобразует строки в словарь, сериализуя datetime объекты."""
    return {key: (value.isoformat() if isinstance(value, datetime) else value) for key, value in row.items()}


async def dump_database(output_file):
    """ Dump data """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")

        dump_data = {}
        for table in tables:
            table_name = table['table_name']
            rows = await conn.fetch(f'SELECT * FROM {table_name}')
            dump_data[table_name] = [serialize_row(dict(row)) for row in rows]

        await conn.close()

        with open(output_file, 'w') as f:
            json.dump(dump_data, f)

        logger.info("Success dump data from service_center")
    except asyncpg.PostgresError as e:
        logger.error(e)
