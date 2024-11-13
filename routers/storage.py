""" Марштруты для страницы склада """

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.storage import insert_data, get_data, update_data
from schemas.component import Component


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/storage")
async def storage_view(request: Request):

    """ отображение страницы скалада, только для админа """

    items = await get_data()

    return templates.TemplateResponse("storage.html", {"request": request, "items": items})


@router.post("/storage")
async def storage_insert(
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

    await insert_data(storage_data.model_dump())
    return RedirectResponse("/storage", status_code=303)


@router.post("/update_inventory")
async def update_inventory(id: int = Form(...), count: int = Form(...)):

    """ обновление значений в базе склада """

    await update_data(id, count)
    return RedirectResponse("/storage", status_code=303)
