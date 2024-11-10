from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from repositories.init_db import init_db
from repositories.user import insert_user, auth_user
import logging
from datetime import datetime
from schemas.user import UserModel


# init
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# DB
DATABASE_URL = "postgresql://postgres:pas@172.17.0.2:5432/service_center"

# hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# session
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    logger.info("Start app")
    await init_db(DATABASE_URL)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


@app.get("/login")
async def login_form(request: Request):
     return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, login: str = Form(...), password: str = Form(...)):
    status = await auth_user(login, password, DATABASE_URL)
    if status is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    request.session['user'] = login
    return RedirectResponse(url="/trouble_tickets", status_code=303)


@app.get("/trouble_tickets", response_class=HTMLResponse)
async def trouble_tickets_page(request: Request):
    if 'user' not in request.session:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return templates.TemplateResponse("tt.html", {"request": request})


@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register/", response_class=HTMLResponse)
async def get_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register/")
async def register_user(
    name: str = Form(...),
    surname: str = Form(...),
    birth_date: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    login: str = Form(...),
    hashed_password: str = Form(...),
):
    # Преобразуем строку даты в объект datetime
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    
    user_data = UserModel(
        name=name,
        surname=surname,
        birth_date=birth_date,
        age=age,
        email=email,
        login=login,
        hashed_password=hashed_password,
    )
    
    user_id = await insert_user(user_data.model_dump(), DATABASE_URL)  # Вставка пользователя в БД
    return RedirectResponse(url="/login", status_code=303)
