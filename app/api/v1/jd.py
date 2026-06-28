import asyncio

from fastapi import APIRouter

from app.api.service.jd_service import jd_parse_service
from app.api.service.llm import llm
from app.models.JD import JDRequests
from app.prompt.jd_parse import jd_system_prompt

jd_router=APIRouter(prefix="/jd",tags=["jd解析"])
@jd_router.post("/parse")
async def jd_parse(requests:JDRequests):
    jd_system_text=jd_system_prompt()
    result=await asyncio.to_thread(jd_parse_service,jd_system_text,requests.jdContent,requests.jdId,requests.jdTitle)
    return result

