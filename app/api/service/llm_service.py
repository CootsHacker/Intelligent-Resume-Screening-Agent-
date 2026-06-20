import os
import re
import json
from datetime import datetime
from openai import OpenAI
from dashscope import Generation

from main import ResumeRequest


#text参数为解析过后的文字
class InvalidJSON(Exception):
    """JSON格式错误(大模型返回数据异常)"""
    pass
class LLMCalledFailed(Exception):
    """大模型调用异常"""
    pass
class LLMParseError(Exception):
    """简历解析失败(代码逻辑或者语法错误)"""
    pass
#定义一个基础数据头结构
basedata={
    "code":0,
    "message":"",
    "data":{
        "resumeId":"",
        "resumeName":"",
        "parseStatus":"",
        "parseResult":"",
        "createTime":""
    }
}
def llm_pdf_parse(text:str,request_data:ResumeRequest) ->json :
    key = os.getenv("DASHSCOPE_API_KEY")
    system_prompt="""
     你是一个专业的HR简历解析助手。请从提供的简历文本中提取关键信息，并严格以JSON格式返回。
    包含以下字段(举例)：
    "basicInfo":{
    "name": "张三",
    "phone": "138****8888",
    "email": "zhangsan@example.com",
    "education": "本科",
    "school": "某某⼤学",
    "major": "计算机科学与技术",
    "graduateTime": "2025-06"
    },
    "skills": ["Java", "Spring Boot", "MySQL", "Redis"],
    "projects": [
    {
    "name": "智学引擎OJ系统",
    "role": "后端开发",
    "time": "2024.03-2024.06",
    "description": "基于Spring Boot的在线编程评测系统..."
    }
    ],
    "workExperience": []
    如果某个字段在文本中未找到，请将其设为 null。不要输出任何额外的解释文字。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请解析以下简历内容：\n{text}"}
    ]
    try:
        response=Generation.call(
            model="qwen-max",
            massages=messages,
            temperature=0.1
        )
        if response.status_code ==200:
            content=response.output.choicesp[0].messages.content
            match=re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                clean_content=match.group()
                data=json.loads(clean_content)
                now = datetime.now()
                time = now.strftime("%Y-%m-%d %H:%M:%S")
                basedata["massage"] = "success"
                basedata["data"]["resumeId"] = request_data.resumeId
                basedata["data"]["resumeName"] = request_data.fileName
                basedata["data"]["parseStatus"] = "success"
                basedata["data"]["parseResult"] = data
                basedata["data"]["createTime"] = time
                return basedata
            else:
                raise InvalidJSON("未能找到合法的JSON数据")
        else:
            raise LLMCalledFailed(f"千问APIdi调用失败:{response.message}")
    except LLMParseError as e:
            raise LLMParseError(f"简历信息提取失败：{e}")