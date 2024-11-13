""" Main app """

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from repositories.init_db import init_db

from routers import auth, storage
from fpdf import FPDF
import logging
from config import DATABASE_URL
from datetime import datetime


# инициализация приложения
app = FastAPI()

# подключение маршрутов
app.include_router(auth.router, tags=["auth"])
app.include_router(storage.router, tags=["storage"])


templates = Jinja2Templates(directory="templates")


# session
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    logger.info("Start app")
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


items = [
    {"id": 1, "name": "Скат", "problem": "Не подключается к интеренету", "date": datetime},
    {"id": 2, "name": "Автоураган", "problem": "Не заапускается от аккамулятора", "date": datetime},
    {"id": 3, "name": "Азимут", "problem": "Разбит корпус", "date": datetime},
]


@app.get("/trouble_tickets", response_class=HTMLResponse)
async def read_table(request: Request):
    return templates.TemplateResponse("table.html", {"request": request, "items": items})


@app.post("/report")
async def create_report(request: Request, item_id: int = Form(...)):
    # Найдите элемент по ID
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return templates.TemplateResponse("report.html", {"request": request, "item": item})
    return {"message": "Элемент не найден"}


@app.post("/submit_report")
async def submit_report(item_id: int = Form(...), description: str = Form(...)):
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        # Создание PDF-файла с использованием FPDF
        pdf_filename = f"report_{item_id}.pdf"
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font('DejaVuSans', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.set_font("DejaVuSans", size=12)
        pdf.cell(200, 10, txt=f"Отчет для элемента с ID: {item_id}", ln=True)
        pdf.cell(200, 10, txt=f"Название: {item['name']}", ln=True)
        pdf.cell(200, 10, txt=f"Проблема: {item['problem']}", ln=True)
        pdf.cell(200, 10, txt=f"Дата: {item['date']}", ln=True)
        pdf.cell(200, 10, txt=f"Дополнительное описание: {description}", ln=True)

        pdf.output(pdf_filename)

    # Возврат PDF-файла пользователю
    return FileResponse(pdf_filename, media_type='application/pdf', filename=pdf_filename)
