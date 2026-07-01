# app/api/v1/resume.py
import asyncio
import time
from asyncio import to_thread
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, Request, Depends

from app.core.embedding.embedding_service import embedding_service
from app.core.vector.Milvus_Client import insert_resumes_to_data
from app.core.vector.insert_to_Milvus import QueueBatchWriter, insert_to_Milvus
from app.models.text_spliter_service import  Data
from app.models.vector_database import VectorData
from app.prompt.pdf_parse import resume_system_prompt
from app.api.service.resume_service import parse_local_pdf
from app.api.service.llm_service import llm_pdf_parse
from app.models.resume import ResumeRequest
from app.utils.text_spliter_service import text_input



router = APIRouter(prefix="/resume", tags=["简历解析"])


@router.post("/parse")
async def parse_pdf(request_data: ResumeRequest):
    # 1. 调用底层解析逻辑（如果出错，会自动被全局异常处理器捕获）
    text = await asyncio.to_thread(parse_local_pdf, request_data.filePath)
    resume_system_text=resume_system_prompt()
    result = await asyncio.to_thread(llm_pdf_parse, text, request_data,resume_system_text)
    # 2. 只有成功时，才在这里组装返回结构
    return {
        **result
    }
#writer: QueueBatchWriter = None
async def get_batch_writer(request: Request) -> QueueBatchWriter:
    return request.app.state.writer
print("=== 正在注册 /vectorize 路由 ===")
#async def get_batch_writer() -> QueueBatchWriter:
   #return writer
@router.post("/vectorize")
async def resume_vectorize(request_data:VectorData,writer: Any = Depends(get_batch_writer)):
    (resumeId,workExperience_chunk,overallSummary_chunk,projects_chunk)=await asyncio.to_thread(text_input,request_data)

    projects_vector,workExperience_vector,overallSummary_vector=await asyncio.gather(
        asyncio.to_thread(embedding_service,projects_chunk),
        asyncio.to_thread(embedding_service,workExperience_chunk),
        asyncio.to_thread(embedding_service,overallSummary_chunk)
    )
    data=await  asyncio.gather(
        asyncio.to_thread(insert_resumes_to_data,resumeId,projects_chunk,projects_vector),
        asyncio.to_thread(insert_resumes_to_data,resumeId,workExperience_chunk,workExperience_vector),
        asyncio.to_thread(insert_resumes_to_data,resumeId,overallSummary_chunk,overallSummary_vector)
    )
    #print(data[0])
    await asyncio.gather(
        writer.add(data[0], "resume_projects"),
        writer.add(data[1], "resume_workExperience"),
        writer.add(data[2], "resume_overallSummary")
    )

