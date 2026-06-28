from app.Exception.Eception import LLMCalledFailed
from app.api.service.llm import llm


def jd_parse_service(system_prompt,text,jdId:str,position:str):
    for i in range(1,4):
        try:
            response=llm(system_prompt,text)
            result={
                "code":0,
                "data":{
                    "jdId":jdId,
                    "position":position,
                    **response
                }
            }
            return result
        except LLMCalledFailed as e:
            if i==3:
                raise LLMCalledFailed({e})
