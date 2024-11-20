""" Маршрут для админа """

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.user import insert_user, auth_user
from schemas.user import UserModel


router = APIRouter()

templates = Jinja2Templates("templates")


@round.get("/admin")
async def admin_root(request: Request):
    """ Страница админа """
    '''
        Тут еще очищение таблицы с документами
        надо будет хранить в сессии роль, чтобы доступ был только у админа.
    '''
    return templates.TemplateResponse("admin.html", {"request": request})