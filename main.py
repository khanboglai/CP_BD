""" Main app """

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from repositories.init_db import init_db

from routers import auth, storage, trouble_tickets, admin, lk


# инициализация приложения
app = FastAPI()

# подключение маршрутов
app.include_router(auth.router, tags=["auth"])
app.include_router(storage.router, tags=["storage"])
app.include_router(trouble_tickets.router, tags=["tt"])
app.include_router(admin.router, tags=['admin'])
app.include_router(lk.router, tags=['lk'])

templates = Jinja2Templates(directory="templates")


# session
app.add_middleware(SessionMiddleware, secret_key="your_secret_key", max_age=3600)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    """ Инициализация базы данных """

    logger.info("Start app")
    # await init_db()


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