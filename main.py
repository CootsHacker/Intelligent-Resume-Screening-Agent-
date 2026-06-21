from datetime import datetime
from fastapi import FastAPI, Request
import time
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.api.service.llm_service import llm_pdf_parse, InvalidJSON, LLMCalledFailed, LLMParseError
# 1. 导入路由
from app.api.v1.resume import router as resume_router, ResumeRequest

# 2. 导入所有自定义异常（建议后续将它们集中放到 app/exceptions.py 中）
from app.api.service.resume_service import PDFParseError, parse_local_pdf
from app.api.service.llm_service import InvalidJSON, LLMCalledFailed, LLMParseError
app = FastAPI()
app.include_router(resume_router, prefix="/agent/api/v1")
def build_error_response(code: int, message: str):
    return JSONResponse(
        status_code=200,  # 保持 HTTP 状态码为 200，由前端根据业务 code 判断
        content={
            "code": code,
            "message": message,
            "data": None,
            "timestamp": int(time.time() * 1000)
        }
    )
#pdf提取
@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    return build_error_response(404, str(exc))

@app.exception_handler(PDFParseError)
async def pdf_parse_error_handler(request: Request, exc: PDFParseError):
    return build_error_response(1001, str(exc))

@app.exception_handler(InvalidJSON)
async def invalid_json_handler(request: Request, exc: InvalidJSON):
    return build_error_response(1004, str(exc))

@app.exception_handler(LLMCalledFailed)
async def llm_called_failed_handler(request: Request, exc: LLMCalledFailed):
    return build_error_response(1002, str(exc))

@app.exception_handler(LLMParseError)
async def llm_parse_error_handler(request: Request, exc: LLMParseError):
    return build_error_response(1005, str(exc))


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
