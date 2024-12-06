""" Маршруты для страницы заявок """

import os
import pytz
import logging
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncpg
import boto3

from repositories.tt import get_data, update_get_row, get_details, cancel_update
from repositories.document import insert_data
from repositories.complex import get_complex
from repositories.works import insert_row
from repositories.storage import get_detail_name, insert_used_detalis
from config import DATABASE_URL
from schemas.document import Document
from pdf_generator import create_pdf


templates = Jinja2Templates(directory="templates")

router = APIRouter()

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


## тестово
s3_client = boto3.client(
    's3',
    endpoint_url='http://storage:9000',
    aws_access_key_id='file_server',  # Замените на ваш Access Key
    aws_secret_access_key='file_server_secret',  # Замените на ваш Secret Key
)

BUCKET_NAME = 'storage-mvs'
try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    logger.warning(f"S3: {e}")


@router.get("/trouble_tickets", response_class=HTMLResponse)
async def read_table(request: Request, id: int = None):
    """ отображение данных на странице """

    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе!"})
    
    error_msg = None
    if id is not None:
        error_msg = "На складе нет деталей для выполнения работы"
        await cancel_update(id)

    items = await get_data()
    info_message = None
    if not items:
        info_message = "Заявок пока нет"
    
    return templates.TemplateResponse("worker/tt.html", {"request": request, "items": items, "message": info_message, "error": error_msg})


@router.post("/report")
async def create_report(request: Request, item_id: int = Form(...)):
    """ Форма для отчета """

    if 'user' not in request.session:
        raise HTTPException(status_code=403, detail="Not authenticated")
    
    item = await update_get_row(item_id)
    complex_item = await get_complex(item['ИСН'])
    details = await get_details(complex_item['name'])

    if item and details:
        return templates.TemplateResponse("worker/report.html", {"request": request, "item": item, "details": details, "error": None})
    return {"message": "Элемент не найден"}


@router.post("/submit_report")
async def submit_report(request: Request, 
                        id: int = Form(...), 
                        complex_id: int = Form(...),
                        problem: str = Form(...),
                        date: str = Form(...),
                        description: str = Form(...), 
                        no_details: int = Form(None),
                        selected_details: list = Form(None)):
    """ Создание отчета """

    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе!"})


    item_data = {
        "id": id,
        "ИСН": complex_id,
        "problem": problem,
        "date": date
    }

    complex_info = await get_complex(complex_id)
    logger.info(f"Comlex info: {complex_info}")

    if selected_details is None and no_details is None:
        details = await get_details(complex_info['name'])
        return templates.TemplateResponse("worker/report.html", {"request": request, "item": item_data, "details": details, "error": "Выберите что-то из списка."})

    if len(description) == 0:
        details = await get_details(complex_info['name'])
        return templates.TemplateResponse("worker/report.html", {"request": request, "item": item_data, "details": details, "error": "Добавьте описание работы!"})

    user = request.session['user']

    timezone = pytz.timezone('Europe/Moscow')
    creation_time = datetime.now(timezone)

    work = {
        "worker_login": user,
        "ИСН": complex_id,
        "finisd_date": creation_time.replace(tzinfo=None),
        "description": description,
        "tt_id": id,
    }

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        async with conn.transaction():

            work_id = await insert_row(conn, work)

            names = []
            if selected_details:
                selected_details = list(map(int, selected_details))
                for detail_id in selected_details: # выдача детаелй, которые были выбраны на фронте и вычитание из таблицы склада
                    names.append(await get_detail_name(conn, detail_id))

                    row_id = await insert_used_detalis(conn, work_id, detail_id)
                    if row_id is None:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Что-то не так с БД")
    except Exception as e:
        logger.error(f"Exception: {e}")
        return RedirectResponse(url=f"/trouble_tickets?id={id}", status_code=303)
    finally:
        await conn.close()
    
    try:
        report_filename = f"report_{uuid.uuid4()}_{item_data['id']}_{creation_time}_{user}.pdf"
        create_pdf(report_filename, item_data, description, names)

        s3_client.upload_file(report_filename, BUCKET_NAME, f"{user}/" + report_filename)

        doc = Document(
            name=report_filename,
            creation_date=creation_time.astimezone(pytz.utc).replace(tzinfo=None),
            file_path=report_filename,
            author_login=request.session.get('user')
        )

        await insert_data(doc)

        os.remove(report_filename)

        logger.info("Created report")
    except Exception as e:
        logger.error(f"Error with report creations: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка при создании отчета.")

    # Возврат PDF-файла пользователю
    return RedirectResponse("/files", status_code=303)


@router.get("/files", response_class=HTMLResponse)
async def read_root(request: Request):
    if 'user' not in request.session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user = request.session.get('user')

    # Получаем список PDF-файлов для конкретного пользователя
    try:
        pdf_files = []
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"{user}/")
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.pdf'):
                pdf_files.append({
                    'key': obj['Key'],
                    'last_modified': obj['LastModified']
                })

        # Сортируем файлы по времени последнего изменения
        pdf_files.sort(key=lambda x: x['last_modified'], reverse=True)  # Сортировка по убыванию времени

    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Credentials not available: {e}")
    
    info_message = None
    if not pdf_files:
        info_message = "Вы еще не создали файлов"
        
    return templates.TemplateResponse("worker/files.html", {"request": request, "pdf_files": [file['key'] for file in pdf_files], "message": info_message})


@router.get("/pdfs/{user}/{pdf_name}")
async def get_pdf(pdf_name: str, request: Request):
    pdf_path = f"{pdf_name}"  # Путь к файлу в MinIO
    try:
        # Получаем файл из MinIO
        user = request.session.get('user')
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{user}/{pdf_path}")
        return StreamingResponse(response['Body'], media_type='application/pdf', headers={"Content-Disposition": f"inline; filename={pdf_name}"})
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found {e}")
