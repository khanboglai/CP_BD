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

    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login(request: Request, login: str = Form(...), password: str = Form(...)):

    """ проверка данных авторизации и перенаправление """

    status = await auth_user(login, password)
    if status == 0:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Пользователя с такими данными не существует"})

    request.session['user'] = login
    request.session['id'] = status['id']
    request.session['role'] = status['usr_role']

    if status['usr_role'] == "admin":
        return RedirectResponse(url="/admin/users", status_code=303)
    return RedirectResponse(url="/trouble_tickets", status_code=303)


@router.get("/logout")
async def logout(request: Request):

    """ выход из учетной записи """

    request.session.pop('user', None)
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register/", response_class=HTMLResponse)
async def get_register_form(request: Request):

    """ отображение страницы регистрации """

    return templates.TemplateResponse("register.html", {"request": request, "error": None, "form_data": {}})


@router.post("/register/")
async def register_user(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    birth_date: str = Form(...),
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
        email=email,
        login=login,
        hashed_password=hashed_password,
        user_role="worker"
    )

    exist_user = await auth_user(login, hashed_password)

    if exist_user:
        return templates.TemplateResponse("register.html", {
        "request": request,
        "error": "Пользователь с таким логином уже существует.",
        "form_data": {
            "name": name,
            "surname": surname,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "email": email,
            "login": login,
        }
    })

    user_id = await insert_user(user_data.model_dump())  # Вставка пользователя в БД
    if user_id is not None:
        return RedirectResponse(url="/admin/users", status_code=303)  
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": "Проверьте данные",
        "form_data": {
            "name": name,
            "surname": surname,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "email": email,
            "login": login,
        }
    })
