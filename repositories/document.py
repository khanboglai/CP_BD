""" Функции для работы с таблицей документов """

import logging
import asyncpg
from config import DATABASE_URL, logger

from schemas.document import Document


async def insert_data(doc: Document):
    try:
        conn = await asyncpg.connect(DATABASE_URL)

        query = """INSERT INTO documents (name, creation_date, file_path, author_login)
        VALUES ($1, $2, $3, $4)
        RETURNING id"""

        doc_id = await conn.fetchval(query, doc.name, doc.creation_date, doc.file_path, doc.author_login)
        await conn.close()
        
        logger.info(f"Created row with id: {doc_id}")
        return doc_id
    except Exception as e:
        logger.error(e)

