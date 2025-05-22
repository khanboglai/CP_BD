import asyncio
import json
from typing import List

from redis.asyncio import Redis
import config
from config import logger

redis_client = Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_SESSION_DB,
    decode_responses=False
)


async def redis_listener(active_connections: List):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("ticket_updates")

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message and message['type'] == 'message':
            data = json.loads(message['data'].decode('utf-8'))
            logger.info(f"Получено сообщение из Redis: {data}")

            for connection in active_connections:
                await connection.send_text(json.dumps(data))
        await asyncio.sleep(0.01)