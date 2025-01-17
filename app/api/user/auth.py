import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.api.models import ResponseModel
from app.schemas.user import User, UserSchema
from core.security import (create_access_token, get_password_hash,
                           verify_password)
from core.utils import load_smtp_config_from_db
from db.session import get_session

auth_router = APIRouter()

class ResetPasswordSchema(BaseModel):
    email: str
    new_password: str

# 添加中间件
def add_session_middleware(app):
    app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

def getRandCode(n):
    return ''.join([str(random.randint(0, 9)) for i in range(n)])

def send_email(subject, body, to_email):
    # 从数据库中获取邮箱配置
    config_dict = load_smtp_config_from_db()
    smtp_server = config_dict.get("smtp_server")  # 邮箱的smtp服务器地址
    smtp_port = config_dict.get("smtp_port")  # 端口号
    smtp_user = config_dict.get("smtp_user")  # 发送邮件的邮箱
    smtp_password = config_dict.get("smtp_password")  # 发送邮件的邮箱的授权码
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")
    finally:
        server.quit()

@auth_router.post("/register", response_model=ResponseModel, tags=["User"])
async def register(
    user: UserSchema,
    request: Request,
    session: AsyncSession = Depends(get_session),
    x_verify_code: str = Header(None)
):
    try:
        # 检查用户名是否已存在
        existing_user = await session.execute(select(User).where(User.username == user.username))
        if existing_user.scalar_one_or_none():
            return ResponseModel(code=1, msg="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = await session.execute(select(User).where(User.email == user.email))
        if existing_email.scalar_one_or_none():
            return ResponseModel(code=1, msg="邮箱已存在")

        # 检查学号是否已存在
        existing_student_id = await session.execute(select(User).where(User.student_id == user.student_id))
        if existing_student_id.scalar_one_or_none():
            return ResponseModel(code=1, msg="学号已存在")

        # 验证码逻辑
        if 'verify_code' in request.session:
            verify_code = request.session['verify_code']

            if not x_verify_code or x_verify_code != verify_code:
                return ResponseModel(code=1, msg="验证码错误")

            # 创建用户
            user_db = User(**user.model_dump())
            user_db.password = get_password_hash(user.password)
            session.add(user_db)
            await session.commit()
            await session.refresh(user_db)

            # 清理 session 中的验证码
            del request.session['verify_code']

            return ResponseModel(code=0, msg="用户注册成功", data=user_db.model_dump())
        else:
            # 生成并发送验证码
            verify_code = getRandCode(6)
            print(verify_code)
            send_email("欢迎注册AI游戏平台", f"验证码是: {verify_code}", user.email)

            # 将验证码存入 session
            request.session['verify_code'] = verify_code
            return ResponseModel(code=0, msg="验证码已发送，请查收")

    except Exception as e:
        return ResponseModel(code=1, msg=f"注册失败: {str(e)}")

class LoginRequest(BaseModel):
    username: str
    password: str
@auth_router.post("/login", response_model=ResponseModel, tags=["User"])
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    username = request.username
    password = request.password
    try:
        # 检查用户是否存在
        user = await session.execute(select(User).where(User.username == username))
        user_db = user.scalar_one_or_none()
        if not user_db or not verify_password(password, user_db.password):
            return ResponseModel(code=1, msg="用户名或密码错误")

        # 创建访问令牌
        access_token = create_access_token(data={"sub": user_db.username})
        return ResponseModel(code=0, msg="登录成功", data={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@auth_router.post("/forgot-password", response_model=ResponseModel, tags=["User"])
async def forgot_password(email: str, request: Request, session: AsyncSession = Depends(get_session)):
    try:
        # 检查用户邮箱是否存在
        existing_email = await session.execute(select(User).where(User.email == email))
        user = existing_email.scalar_one_or_none()
        if not user:
            return ResponseModel(code=1, msg="邮箱不存在")

        # 生成验证码并发送邮件
        reset_code = getRandCode(6)
        send_email("重置密码请求", f"验证码是: {reset_code}", email)

        # 将验证码存储到 session
        request.session['reset_code'] = reset_code
        request.session['email'] = email

        return ResponseModel(code=0, msg="重置验证码已发送，请检查您的邮箱")

    except Exception as e:
        return ResponseModel(code=1, msg=f"发送重置密码验证码失败: {str(e)}")


@auth_router.post("/reset-password", response_model=ResponseModel, tags=["User"])
async def reset_password(
    reset_password_data: ResetPasswordSchema,
    request: Request,
    x_reset_code: str = Header(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        # 从 session 中获取验证码和邮箱
        session_reset_code = request.session.get("reset_code")
        session_email = request.session.get("email")

        if not session_reset_code or not session_email:
            return ResponseModel(code=1, msg="没有找到验证码或邮箱")

        # 检查验证码是否正确
        print(x_reset_code,session_reset_code)
        if not x_reset_code or x_reset_code != session_reset_code:
            return ResponseModel(code=1, msg="验证码错误")

        # 检查请求中的邮箱是否与 session 中的邮箱匹配
        if reset_password_data.email != session_email:
            return ResponseModel(code=1, msg="邮箱与验证码不匹配")

        # 更新用户的密码
        existing_user = await session.execute(select(User).where(User.email == reset_password_data.email))
        user = existing_user.scalar_one_or_none()
        if not user:
            return ResponseModel(code=1, msg="用户不存在")

        user.password = get_password_hash(reset_password_data.new_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # 清除 session 中的验证码
        del request.session['reset_code']
        del request.session['email']

        return ResponseModel(code=0, msg="密码重置成功")

    except Exception as e:
        return ResponseModel(code=1, msg=f"重置密码失败: {str(e)}")