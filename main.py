from fastapi import FastAPI, Depends, APIRouter, Request, Cookie
import models
from database import engine
#from routers import chat_v2 as chat
from routers import auth
from starlette.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import get_current_user_cookie, get_current_user
from jose import jwt
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/",response_class=HTMLResponse)
async def render_homepage(request: Request):
    try: 
        user = await get_current_user(request.cookies.get('access_token'))
    except:
        user = None
    return templates.TemplateResponse('home.html',{"request":request,"name":user['name']+"님 안녕하세요!" if user else "안녕하세요!"})

@app.get("/test",response_class=HTMLResponse)
async def test(request: Request):
    current_user = await get_current_user_cookie(request.cookies.get('access_token'))
    if current_user:
        return templates.TemplateResponse('test.html', {"request": request})
    else:
        return RedirectResponse(url="/login")
    

@app.get("/register",response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('register.html',{"request":request})

@app.get("/login",response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('login.html',{"request":request})
#app.include_router(chat.router)
app.include_router(auth.router)