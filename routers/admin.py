""" Маршрут для админа """

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates



router = APIRouter()

templates = Jinja2Templates("templates")


@router.get("/admin", response_class=HTMLResponse)
async def admin_root(request: Request):
    """ Страница админа """
    
    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе"})

    role = request.session.get('role')
    if role != "admin":
        return templates.TemplateResponse("login.html", {"request": request, "error": "У вас нет прав для посещения этой страницы"})
    
    return templates.TemplateResponse("admin.html", {"request": request})
