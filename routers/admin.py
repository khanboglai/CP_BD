""" Маршрут для админа """

import io
import logging
from datetime import datetime

import pandas as pd

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import boto3

from repositories.user import get_users, delete_user, get_user, update_usr
from repositories.complex import *
from repositories.files import get_files
from repositories.works import get_data
from repositories.analitic import get_analitic, delete_analitic

from schemas.complex import ComplexModel, UpdateComplexModel
from schemas.user import UpdateUserModel

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
        return templates.TemplateResponse("admin/users.html", {"request": request, "employees": employees})
    return {"message": "Some problems"}


@router.get("/admin/files")
async def admin_files(request: Request):

    # check users

    files = await get_files()

    return templates.TemplateResponse("admin/doc.html", {"request": request, "files": files})


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
        return templates.TemplateResponse("admin/midlle_delet.html", {"request": request})
    
    st = await delete_user(login)
    if st:
        return RedirectResponse(url="/admin/users", status_code=303)
    raise HTTPException(status_code=404, detail="Проблемы с БД")


@router.get("/complexes", response_class=HTMLResponse)
async def show_complexes(request: Request):
    """ Функция для отображения комплексов """

    user = request.session.get('user')
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе"})

    data = await get_complexes()
    if data:
        return templates.TemplateResponse("admin/complexes.html", {"request": request, "complexes": data})
    raise HTTPException(status_code=404, detail="Доделать надо чтобы перенаправляло")


@router.post("/del/{id}")
async def delete_complex(request: Request, id: int):
    user = request.session.get('user')
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Авторизуйтесь в системе"})
    
    st = await del_complex(id)
    if st:
        return RedirectResponse(url="/complexes", status_code=303)
    raise HTTPException(status_code=404, detail="Проблемы с БД")


@router.get("/add_complex", response_class=HTMLResponse)
async def send_form_complex(request: Request):
    """ Функция для отображения формы для добавления комплекса """

    return templates.TemplateResponse("admin/insert_complex.html", {"request": request, "error": None, "form_data": {}})


@router.post("/add_complex")
async def insert_complex(request: Request,
                        ИСН: int = Form(...),
                        name: str = Form(...),
                        factory_id: int = Form(...),
                        creation_date: str = Form(...)):
    """ Добавленик комплекса в базу """

    creation_date = datetime.strptime(creation_date, "%Y-%m-%d")

    complex_data = ComplexModel(
        ISN=ИСН,
        name=name,
        factory_id=factory_id,
        creation_date=creation_date
    )

    check = await check_complex(ИСН)
    if check:
        return templates.TemplateResponse("admin/insert_complex.html", {"request": request, "error": "Коплекс с таким ИСН уже существует", "form_data": complex_data})
    
    res = await insert_complex_data(complex_data)
    if res:
        return RedirectResponse(url="/complexes", status_code=303)
    return templates.TemplateResponse("admin/insert_complex.html", {
        "request": request,
        "error": "Проверьте данные",
        "form_data": complex_data
    })


@router.get("/works", response_class=HTMLResponse)
async def show_works(request: Request):
    """ Функция для отображения работ """

    data = await get_data()

    return templates.TemplateResponse("admin/works.html", {"request": request, "items": data})


@router.get("/edit_complex/{id}", response_class=HTMLResponse)
async def show_edit_page_complex(request: Request, id: int):
    """ Функция для отображения страницы редактирования комплекса """

    complex_data = await get_complex(id)
    if not complex_data:
        raise HTTPException(status_code=404, detail="Complex not found")
    
    return templates.TemplateResponse("admin/edit_complexes.html", {"request": request, "complex": complex_data, "complex_id": id})


@router.post("/update_complex/{id}")
async def update_complex(request: Request, id: int, name: str = Form(...), factory_id: int = Form(...), creation_date: str = Form(...)):
    """ Функция для обновления данных комплекса """

    # if complex_id not in complexes:
    #     raise HTTPException(status_code=404, detail="Complex not found")

    data = UpdateComplexModel(
        name = name,
        factory_id=factory_id,
        creation_date=creation_date,
    )

    res = await update_row(id, data)
    if res:
        return RedirectResponse(url="/complexes", status_code=303)
    
    raise HTTPException(status_code=404, detail="Проблема с обновлением данных!")


@router.get("/edit_user/{login}", response_class=HTMLResponse)
async def show_edit_page_user(request: Request, login: str):
    """ Функция для отображения страницы редактирования комплекса """

    user_data = await get_user(login)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("admin/edit_users.html", {"request": request, "user": user_data, "user_id": id})


@router.post("/update_user/{id}")
async def update_user(request: Request, id: int, data: UpdateUserModel = Form(...)):
    """ Функция для обновления данных комплекса """

    # if complex_id not in complexes:
    #     raise HTTPException(status_code=404, detail="Complex not found")

    res = await update_usr(id, data)
    if res:
        return RedirectResponse(url="/admin/users", status_code=303)
    
    raise HTTPException(status_code=404, detail="Проблема с обновлением данных!")


@router.get("/analitic", response_class=HTMLResponse)
async def show_analitic(request: Request):
    """ Функция для отображения аналитики """

    res = await get_analitic()
    return templates.TemplateResponse("admin/analitic.html", {"request": request, "data": res})

@router.get("/kill_analitic")
async def kill_analitic():
    data = await delete_analitic()

    return RedirectResponse(url="/analitic", status_code=303)


@router.get("/export_users/csv")
async def export_users_csv():
    data = await get_users()

    # Преобразуйте данные в DataFrame
    df = pd.DataFrame(data)

    # Создайте CSV файл в памяти
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Верните CSV файл как ответ
    return Response(content=csv_buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export_users.csv"})


@router.get("/export_complexes/csv")
async def export_complexes_csv():
    data = await get_complexes()

    # Преобразуйте данные в DataFrame
    df = pd.DataFrame(data)

    # Создайте CSV файл в памяти
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Верните CSV файл как ответ
    return Response(content=csv_buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export_complexes.csv"})


@router.get("/export_works/csv")
async def export_works_csv():
    data = await get_data()

    # Преобразуйте данные в DataFrame
    df = pd.DataFrame(data)

    # Создайте CSV файл в памяти
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Верните CSV файл как ответ
    return Response(content=csv_buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export_works.csv"})
