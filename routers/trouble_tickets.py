""" Маршруты для страницы заявок """

import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fpdf import FPDF

from repositories.tt import get_data, update_get_row, get_row, get_details


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/trouble_tickets", response_class=HTMLResponse)
async def read_table(request: Request):
    """ отображение данных на странице """

    if 'user' not in request.session:
        raise HTTPException(status_code=403, detail="Not authenticated")

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
        return templates.TemplateResponse("report.html", {"request": request, "item": item, "details": details})
    return {"message": "Элемент не найден"}


@router.post("/submit_report")
async def submit_report(request: Request, id: int = Form(...), description: str = Form(...), 
                        details: list = Form(...)):
    """ Создание отчета """

    if 'user' not in request.session:
        raise HTTPException(status_code=403, detail="Not authenticated")
    
    # selected_details = []
    # for detail_id in details:
    #     # Найдите соответствующее имя для каждого ID
    #     index = int(detail_id) - 1  # Предполагается, что ID начинаются с 1
    #     selected_details.append({
    #         "id": detail_id,
    #         "name": detail_names[index]
    #     })
    
    user = request.session['user']

    item = await get_row(id)

    if item:
        # Создание PDF-файла с использованием FPDF
        pdf_filename = f"report_{id}_{user}.pdf"
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font('DejaVuSans', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.set_font("DejaVuSans", size=12)
        pdf.cell(200, 10, txt=f"Отчет для элемента с ID: {id}", ln=True)
        pdf.cell(200, 10, txt=f"Название: {item['name']}", ln=True)
        pdf.cell(200, 10, txt=f"Проблема: {item['problem']}", ln=True)
        pdf.cell(200, 10, txt=f"Дата: {item['date']}", ln=True)
        pdf.cell(200, 10, txt=f"Дополнительное описание: {description}", ln=True)
        print(details)
        pdf.cell(200, 10, txt=f"Список деталей: {details}", ln=True)

        pdf.output(pdf_filename)

        # тут еще будет логика с сохранением данных о работе в таблицу

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
