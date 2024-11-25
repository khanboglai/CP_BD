""" Маршруты для страницы заявок """

import os
import json

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fpdf import FPDF

from repositories.tt import get_data, update_get_row, get_row, get_details, update_get_detail


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
    selected_details = list(map(int, selected_details))
    if selected_details is not None:
        for detail_id in selected_details: # выдача детаелй, которые были выбраны на фронте и вычитание из таблицы склада
            names.append(await update_get_detail(detail_id))
    

    try:
        # Создание PDF-файла с использованием FPDF

        ''' Убрать этот блок в отдельный файлё '''
        pdf_filename = f"report_{id}_{user}.pdf"
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font('DejaVuSans', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.set_font("DejaVuSans", size=12)
        pdf.cell(200, 10, txt=f"Отчет для элемента с ID: {id}", ln=True)
        pdf.cell(200, 10, txt=f"Название: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Проблема: {problem}", ln=True)
        pdf.cell(200, 10, txt=f"Дата: {date}", ln=True)
        pdf.cell(200, 10, txt=f"Дополнительное описание: {description}", ln=True)
        pdf.cell(200, 10, txt=f"Список деталей: {', '.join(names)}", ln=True)

        pdf.output(pdf_filename)

        # тут еще будет логика с сохранениемdetails данных о работе в таблицу
    except Exception as e:
        return {"message": "Невозможно создать файл!"}

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
