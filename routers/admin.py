""" Маршрут для админа """

import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from repositories.user import get_users
from repositories.files import get_files

router = APIRouter()

templates = Jinja2Templates("templates")


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
    if files:
        return templates.TemplateResponse("doc.html", {"request": request, "files": files})
    content = {"message": "Something went wrong"}
    return content


@router.get("/admin/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
