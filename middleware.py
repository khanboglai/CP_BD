from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from redis_session import redis_client
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class RedisSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Получаем session_id из куков
        session_id = request.cookies.get("session_id")

        if not session_id:
            # Если session_id отсутствует, создаем новый
            session_id = str(uuid.uuid4())
            request.state.session = {}  # Создаем пустую сессию
        else:
            # Если session_id есть, загружаем данные сессии из Redis
            session_data = await redis_client.get(f"session:{session_id}")
            try:
                request.state.session = json.loads(session_data) if session_data else {}
            except (json.JSONDecodeError, TypeError):
                logger.error("Ошибка при загрузке данных сессии из Redis")
                request.state.session = {}

        # Передаем управление следующему обработчику
        response = await call_next(request)

        # Сохраняем данные сессии обратно в Redis
        if hasattr(request.state, "session"):
            try:
                session_json = json.dumps(request.state.session)
                logger.info(f"Сохраняем в Redis: {session_json}")
                await redis_client.set(
                    f"session:{session_id}",
                    session_json,
                    ex=3600
                )
            except Exception as e:
                logger.error(f"Ошибка при сохранении в Redis: {e}")

            # Устанавливаем session_id в куки
            response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=3600)

        return response