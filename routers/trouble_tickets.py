""" Маршруты для страницы заявок """

import os
import pytz
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates


from repositories.tt import get_data, update_get_row, get_details, update_get_detail
from repositories.document import insert_data
from schemas.document import Document
from pdf_generator import create_pdf

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/trouble_tickets", response_class=HTMLResponse)
async def read_table(request: Request):
    """ отображение данных на странице """

    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе!"})

    items = await get_data()
    if items is not None:
        return templates.TemplateResponse("table.html", {"request": request, "items": items})
    return {"message": "Данные не найдены"}


@router.post("/report")
async def create_report(request: Request, item_id: int = Form(...)):
    """ Форма для отчета """

    if 'user' not in request.session:
        raise HTTPException(status_code=403, detail="Not authenticated")
    
    item = await update_get_row(item_id)
    details = await get_details(item['name'])

    if item and details:
        return templates.TemplateResponse("report.html", {"request": request, "item": item, "details": details, "error": None})
    return {"message": "Элемент не найден"}


@router.post("/submit_report")
async def submit_report(request: Request, 
                        id: int = Form(...), 
                        name: str = Form(...),
                        problem: str = Form(...),
                        date: str = Form(...),
                        description: str = Form(...), 
                        no_details: int = Form(None),
                        selected_details: list = Form(None)):
    """ Создание отчета """

    item_data = {
        "id": id,
        "name": name,
        "problem": problem,
        "date": date
    }

    if selected_details is None and no_details is None:
        details = await get_details(name)
        return templates.TemplateResponse("report.html", {"request": request, "item": item_data, "details": details, "error": "Выберите что-то из списка."})


    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе!"})
    

    user = request.session['user']

    names = []
    if selected_details is not None:
        selected_details = list(map(int, selected_details))
        for detail_id in selected_details: # выдача детаелй, которые были выбраны на фронте и вычитание из таблицы склада
            names.append(await update_get_detail(detail_id))
    

    try:
        timezone = pytz.timezone('Europe/Moscow')
        creation_time = datetime.now() # Разобраться с локализацией времени, проблема с БД``
        report_filename = f"report_{uuid.uuid4()}_{item_data['id']}_{creation_time}_{user}.pdf"
        create_pdf(report_filename, item_data, description, names)


        doc = Document(
            name=report_filename,
            creation_date=creation_time,
            file_path=report_filename,
            author_id=request.session.get('id')
        )

        await insert_data(doc)

        # тут еще будет логика с сохранениемdetails данных о работе в таблицу
    except Exception as e:
        return {"message": e}

    # Возврат PDF-файла пользователю
    return RedirectResponse("/files", status_code=303)


@router.get("/files", response_class=HTMLResponse)
async def read_root(request: Request):
    # Получаем список PDF-файлов

    if 'user' not in request.session:
        raise HTTPException(status_code=403, detail="Not authenticated")
    
    user = request.session['user']

    pdf_files = [f for f in os.listdir() if f.endswith(f'{user}.pdf')]
    return templates.TemplateResponse("files.html", {"request": request, "pdf_files": pdf_files})


@router.get("/pdfs/{pdf_name}")
async def get_pdf(pdf_name: str):
    pdf_path = os.path.join("", pdf_name)
    return FileResponse(pdf_path)
