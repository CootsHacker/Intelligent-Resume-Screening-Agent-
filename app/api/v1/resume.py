# app/api/v1/resume.py
import time
from fastapi import APIRouter
from app.api.service.resume_service import parse_local_pdf
from app.api.service.llm_service import llm_pdf_parse
from app.models.resume import ResumeRequest

router = APIRouter(prefix="/resume", tags=["简历解析"])





@router.post("/parse")
async def parse_pdf(request_data: ResumeRequest):
    # 1. 调用底层解析逻辑（如果出错，会自动被全局异常处理器捕获）
    text = parse_local_pdf(request_data.filepath)
    result = llm_pdf_parse(text, request_data)

    # 2. 只有成功时，才在这里组装返回结构
    return {
        "code": 200,
        "message": "success",
        "data": result,
        "timestamp": int(time.time() * 1000)
    }