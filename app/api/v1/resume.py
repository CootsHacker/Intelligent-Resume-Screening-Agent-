# app/api/v1/resume.py
import asyncio
import time
from asyncio import to_thread
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI,Request

from app.core.embedding.embedding_service import embedding_service
from app.core.vector.Milvus_Client import insert_resumes_to_data
from app.core.vector.insert_to_Milvus import QueueBatchWriter, insert_to_Milvus
from app.models.text_spliter_service import ResumeText
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
    print(resume_system_text)
    print(text)
    result = await asyncio.to_thread(llm_pdf_parse, text, request_data,resume_system_text)
    # 2. 只有成功时，才在这里组装返回结构
    return {
        **result
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    writer = QueueBatchWriter(max_size=10, timeout=3.0, write_func=insert_to_Milvus)
    await writer.start()
    yield {"writer": writer}
    await writer.shutdown()
app = FastAPI(lifespan=lifespan)
@router.post("/vectorize")
async def resume_vectorize(request: Request,request_data:ResumeText):
    (baseInfo_dict,skills_dict,education_dict,projects_chunk,awards_text,
     overallSummary_chunk,workExperience_chunk,resumeId)=await asyncio.to_thread(text_input,request_data)

    projects_vector,workExperience_vector,overallSummary_vector=await asyncio.gather(
        asyncio.to_thread(embedding_service,projects_chunk),
        asyncio.to_thread(embedding_service,workExperience_chunk),
        asyncio.to_thread(embedding_service,overallSummary_chunk)
    )
    data=await asyncio.to_thread(insert_resumes_to_data,resumeId,baseInfo_dict,
                            skills_dict,education_dict,projects_vector,awards_text,overallSummary_vector,workExperience_vector)
    writer: QueueBatchWriter = request.state.writer
    await writer.add(data)

