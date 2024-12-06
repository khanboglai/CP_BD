import asyncpg
import json
from datetime import datetime
from config import DATABASE_URL_ADM
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deserialize_row(row):
    """Преобразует строки обратно в оригинальные типы, включая datetime."""
    for key, value in row.items():
        if isinstance(value, str):
            try:
                # Попробуем преобразовать строку в datetime
                row[key] = datetime.fromisoformat(value)
            except ValueError:
                pass  # Если не удалось, оставляем как есть
    return row


async def restore_database(input_file):
    """ Restore data """

    try:
        conn = await asyncpg.connect(DATABASE_URL_ADM)

        with open(input_file, 'r') as f:
            dump_data = json.load(f)

        # Сначала вставляем данные в родительские таблицы
        for table_name in dump_data.keys():
            if table_name == "works":  # Предположим, что "works" - это родительская таблица
                for row in dump_data[table_name]:
                    row = deserialize_row(row)
                    columns = ', '.join(row.keys())
                    values = ', '.join(f"${i+1}" for i in range(len(row)))
                    query = f'INSERT INTO {table_name} ({columns}) VALUES ({values})'
                    await conn.execute(query, *row.values())

        # Затем вставляем данные в дочерние таблицы
        for table_name in dump_data.keys():
            if table_name != "works":  # Пропускаем родительскую таблицу
                for row in dump_data[table_name]:
                    row = deserialize_row(row)
                    columns = ', '.join(row.keys())
                    values = ', '.join(f"${i+1}" for i in range(len(row)))
                    query = f'INSERT INTO {table_name} ({columns}) VALUES ({values})'
                    await conn.execute(query, *row.values())

        await conn.close()
    except asyncpg.PostgresError as e:
        logger.error(e)
