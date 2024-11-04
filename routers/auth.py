from fastapi import APIRouter, Response
from pydantic import BaseModel
from passlib.context import CryptContext
from database import SessionLocal
from models import Users
from sqlalchemy.orm import Session
from fastapi import Depends, Cookie
from typing import Annotated
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta,datetime,timezone
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)

SECRETE_KEY = "14jfklasdfjaldskfj124jkasdfljsdaf"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    email: str
    name: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]

def create_access_token(username:str,name:str, user_id:int, expires_delta:timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": username, "name":name, "id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return credentials_exception
    except JWTError:
        return credentials_exception
    return {'username':username,'name':payload.get("name"),'id':payload.get("id")} 

async def get_current_user_cookie(token: str = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if(token is None):
        return None
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    return {'username':username,'name':payload.get("name"),'id':payload.get("id")} 


@router.post("/register")
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = db.query(Users).filter(Users.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    create_user_model = Users(name = create_user_request.name, email=create_user_request.email, hashed_password=bcrypt_context.hash(create_user_request.password))
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model


@router.post("/token")
async def login(response:Response, db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(Users).filter(Users.email == form_data.username).first() #here username of formdata refers to email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email"
        )
    if not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    access_token = create_access_token(user.email, user.name, user.id, timedelta(minutes=30))
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800)

    return {"access_token": access_token, "token_type": "bearer"}