""" Маршрут для админа """

import os
import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import boto3

from repositories.user import get_users, delete_user
from repositories.files import get_files

router = APIRouter()

templates = Jinja2Templates("templates")

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# подключение к s3
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


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    """ Страница админа """
    
    if 'user' not in request.session:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе"})

    role = request.session.get('role')
    if role != "admin":
        return templates.TemplateResponse("login.html", {"request": request, "error": "У вас нет прав для посещения этой страницы"})
    
    employees = await get_users()
    
    if employees:
        return templates.TemplateResponse("admin.html", {"request": request, "employees": employees})
    return {"message": "Some problems"}


@router.get("/admin/files")
async def admin_files(request: Request):

    # check users

    files = await get_files()

    return templates.TemplateResponse("doc.html", {"request": request, "files": files})


@router.get("/admin/{filename}")
async def download_file(filename: str, request: Request):
    user = request.session.get('user')
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе"})

    filename_without_extension = filename[:-4]
    # Разделяем строку по символу '_'
    parts = filename_without_extension.split('_')
    # Имя пользователя находится в последней части
    username = parts[-1]

    # Путь к файлу в S3
    s3_key = f"{username}/{filename}"

    try:
        # Получаем файл из S3
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        return StreamingResponse(
            response['Body'],
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"inline; filename={filename}"} # inline чтобы не скачивалось
        )
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {e}")


@router.post("/delete/{login}")
async def delete_usr(request: Request, login: str):
    """ Функция для удаления пользователя """

    user = request.session.get('user')
    if user == login:
        return templates.TemplateResponse("midlle_delet.html", {"request": request})
    
    st = await delete_user(login)
    if st:
        return RedirectResponse(url="/admin/users", status_code=303)
    raise HTTPException(status_code=404, detail="Проблемы с БД")
