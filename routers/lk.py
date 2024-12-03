""" Маршрут для личного кабинета """

import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from repositories.user import get_user

router = APIRouter()

templates = Jinja2Templates("templates")

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/lk", response_class=HTMLResponse)
async def lk(request: Request):
    """ Функция для отображения личного кабиента """

    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе"})
    
    user = request.session.get('user')
    res = await get_user(user)

    if res:
        return templates.TemplateResponse("lk.html", {"request": request, "user": res})
    return HTTPException(status_code=404, detail="Данных нет")
