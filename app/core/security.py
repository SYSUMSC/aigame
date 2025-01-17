from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl=f"{settings.API_ADMIN_STR}/login")
oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl=f"{settings.API_USER_STR}/login")

async def get_current_user(request: Request):
    access_token = None
    # 先尝试从请求头中获取 access_token
    if "access_token" in request.headers:
        access_token = request.headers["access_token"]
    elif request.method == "POST":
        if "application/json" in request.headers.get("Content-Type", ""):
            # 从 POST 请求体中获取 access_token (JSON body)
            access_token = (await request.json()).get("access_token")
        elif "application/x-www-form-urlencoded" in request.headers.get("Content-Type", ""):
            # 从 POST 请求体中获取 access_token (表单)
            form = await request.form()
            access_token = form.get("access_token")
    elif request.method == "GET":
        # 从 GET 请求参数中获取 access_token
        access_token = request.query_params.get("access_token")
    if not access_token:
        return JSONResponse(
            status_code=200,
            content={
                "code": 1,
                "msg": "未授权，没传输access_token",
                "data": None
            }
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

async def get_current_admin(token: str = Depends(oauth2_scheme_admin)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):
    return pwd_context.hash(password)