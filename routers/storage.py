""" Марштруты для страницы склада """

from fastapi import APIRouter, Form, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import io
from repositories.storage import insert_data, get_data, update_data, delete_data, get_row
from schemas.component import Component


templates = Jinja2Templates(directory="templates")

router = APIRouter()


async def verify_admin(request: Request):
    if 'user' not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=401, detail="Not authenticated how admin")


@router.get("/storage")
async def storage_view(request: Request, admin: None = Depends(verify_admin)):
    """ отображение страницы скалада """

    items = await get_data()
    if items:
        return templates.TemplateResponse("admin/storage.html", {"request": request, "items": items})
    raise HTTPException(status_code=404, detail="Нет данных")


@router.post("/storage")
async def storage_insert(
    request: Request,
    name: str = Form(),
    count: int = Form(),
    complex_name: str = Form(),
    admin: None = Depends(verify_admin)
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
async def update_inventory(request: Request, id: int = Form(...), count: int = Form(...), admin: None = Depends(verify_admin)):

    """ обновление значений в базе склада """

    st = await update_data(id, count)
    if st:
        return RedirectResponse("/storage", status_code=303)
    raise HTTPException(status_code=404, detail="Невозможно обновить значения")


@router.post("/deletedetail/{id}")
async def delete_detail(request: Request, id: int, admin: None = Depends(verify_admin)):
    """ Функция для удаления деталей склада """

    st = await delete_data(id)
    if st:
        return RedirectResponse("/storage", status_code=303)
    raise HTTPException(status_code=404, detail="Невозможно удалить деталь")


@router.get("/export_details/csv")
async def export_details_csv(request: Request, admin: None = Depends(verify_admin)):
    """ Экспорт таблицы деталей """
    
    data = await get_data()

    # Преобразуйте данные в DataFrame
    df = pd.DataFrame(data)

    # Создайте CSV файл в памяти
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Верните CSV файл как ответ
    return Response(content=csv_buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export_details.csv"})
