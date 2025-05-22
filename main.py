""" Main app """
import asyncio

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.websockets import WebSocketDisconnect

from middleware import RedisSessionMiddleware
from contextlib import asynccontextmanager
from routers import auth, storage, trouble_tickets, admin, lk
from config import logger
from redis_session import redis_listener


active_connections = []

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Start app")
    asyncio.create_task(redis_listener(active_connections))
    logger.info("Redis Listener up")
    yield
    logger.info("Stop app")


# инициализация приложения
app = FastAPI(title="Сервисный центр",lifespan=lifespan)

# подключение маршрутов
app.include_router(auth.router, tags=["auth"])
app.include_router(storage.router, tags=["storage"])
app.include_router(trouble_tickets.router, tags=["tt"])
app.include_router(admin.router, tags=['admin'])
app.include_router(lk.router, tags=['lk'])

templates = Jinja2Templates(directory="templates")


# session
app.add_middleware(RedisSessionMiddleware)



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        active_connections.remove(websocket)
        logger.info(f"{e}")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """ Отображение начальной страницы """
    return templates.TemplateResponse("welcome.html", {"request": request})


# обработчик для не существующего маршрута
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return RedirectResponse(url="/") # перенаправление на главную


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("errors/404.html", {"request": request, "error": exc.detail})
    
    if exc.status_code == 401 and exc.detail == "Not authenticated":
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе!"})
    elif exc.status_code == 401 and exc.detail == "Not authenticated how admin":
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе как админ!"})
    
    return HTMLResponse(content="Internal Server Error", status_code=500)