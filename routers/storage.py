""" Марштруты для страницы склада """

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.storage import insert_data, get_data, update_data, delete_data, get_row
from schemas.component import Component


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/storage")
async def storage_view(request: Request):
    """ отображение страницы скалада """

    user = request.session.get('user')
    if user is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизируйтесь в системе!"})
    
    role = request.session.get("role")
    if role != "admin":
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизируйтесь в системе как администратор!"})

    items = await get_data()
    if items:
        return templates.TemplateResponse("admin/storage.html", {"request": request, "items": items})
    raise HTTPException(status_code=404, detail="Нет данных")


@router.post("/storage")
async def storage_insert(
    request: Request,
    name: str = Form(),
    count: int = Form(),
    complex_name: str = Form()
):
    """ сохранение компонент в базе """

    storage_data = Component(
        name=name,
        count=count,
        complex_name=complex_name
    )

    check = await get_row(complex_name)
    if check is None:
        return templates.TemplateResponse("admin/insert_complex.html", {"request": request, "error": "Добавьте комплекс в базу и вернитесь для повторной отправки данных", "form_data": {}})

    st = await insert_data(storage_data.model_dump())
    if st:
        return RedirectResponse("/storage", status_code=303)
    raise HTTPException(status_code=404, detail="Невозможно добавить данные")


@router.post("/update_inventory")
async def update_inventory(request: Request, id: int = Form(...), count: int = Form(...)):

    """ обновление значений в базе склада """

    user = request.session.get('user')
    if user is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизируйтесь в системе!"})
    
    role = request.session.get("role")
    if role != "admin":
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизируйтесь в системе как администратор!"})

    st = await update_data(id, count)
    if st:
        return RedirectResponse("/storage", status_code=303)
    raise HTTPException(status_code=404, detail="Невозможно обновить значения")


@router.post("/deletedetail/{id}")
async def delete_detail(request: Request, id: int):
    """ Функция для удаления деталей склада """

    st = await delete_data(id)
    if st:
        return RedirectResponse("/storage", status_code=303)
    raise HTTPException(status_code=404, detail="Невозможно удалить деталь")
