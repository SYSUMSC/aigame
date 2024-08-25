from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=200,
            content={
                "code": 1,
                "msg": exc.detail,
                "data": None
            }
        )
    elif isinstance(exc, RequestValidationError) or isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=200,
            content={
                "code": 1,
                "msg": "请求参数验证失败",
                "data": exc.errors()
            }
        )
    else:
        return JSONResponse(
            status_code=200,
            content={
                "code": 1,
                "msg": str(exc),
                "data": None
            }
        )