import os
import re
import json
from datetime import datetime
from openai import OpenAI
from dashscope import Generation

from app.Exception.Eception import InvalidJSON, LLMCalledFailed, LLMParseError
from app.models.resume import ResumeRequest


#from resume import ResumeRequest


#text参数为解析过后的文字

#定义一个基础数据头结构
basedata={
    "code":0,
    "message":"",
    "data":{
        "resumeId":"",
        "parseSuccess":""
    }
}
def llm_pdf_parse(text:str,request_data:ResumeRequest,system_prompt) ->json :
    key = os.getenv("DASHSCOPE_API_KEY")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请解析以下简历内容：\n{text}"}
    ]
    try:
        response=Generation.call(
            model="qwen-max",
            messeges=messages,
            temperature=0.1
        )
        # app/api/service/llm_service.py
        if response.status_code ==200:
            content=response.output.text
            match=re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                clean_content=match.group()
                data=json.loads(clean_content)
                now = datetime.now()
                time = now.strftime("%Y-%m-%d %H:%M:%S")
                basedata["message"] = "success"
                basedata["data"]["resumeId"] = request_data.resumeId
                basedata["data"]["parseSuccess"] ="true"
                basedata["data"].update(data)
                return basedata
            else:
                raise InvalidJSON("未能找到合法的JSON数据")
        else:
            raise LLMCalledFailed(f"千问APIdi调用失败:{response.message}")
    except LLMParseError as e:
            raise LLMParseError(f"简历信息提取失败：{e}")