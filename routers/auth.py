""" Маршруты для авторизации и регистрации пользователя """

import logging
from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.user import insert_user, auth_user
from schemas.user import UserModel


# подключение шаблонов
templates = Jinja2Templates(directory="templates")

# создание роутера
router = APIRouter()


@router.get("/login")
async def login_form(request: Request):

    """ отображение страницы авторизации """

    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, login: str = Form(...), password: str = Form(...)):

    """ проверка данных авторизации и перенаправление """

    status = await auth_user(login, password)
    if status is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    request.session['user'] = login
    return RedirectResponse(url="/trouble_tickets", status_code=303)


@router.get("/logout")
async def logout(request: Request):

    """ выход из учетной записи """

    request.session.pop('user', None)
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register/", response_class=HTMLResponse)
async def get_register_form(request: Request):

    """ отображение страницы регистрации """

    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/")
async def register_user(
    name: str = Form(...),
    surname: str = Form(...),
    birth_date: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    login: str = Form(...),
    hashed_password: str = Form(...),
):
    """ сохранение данных в базе """

    # Преобразуем строку даты в объект datetime
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    
    user_data = UserModel(
        name=name,
        surname=surname,
        birth_date=birth_date,
        age=age,
        email=email,
        login=login,
        hashed_password=hashed_password,
    )

    await insert_user(user_data.model_dump())  # Вставка пользователя в БД
    return RedirectResponse(url="/login", status_code=303)
