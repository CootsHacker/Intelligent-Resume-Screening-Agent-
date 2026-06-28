import json
import os
import re

from dashscope import Generation
from json_repair import repair_json

from app.Exception.Eception import InvalidJSON, LLMCalledFailed


def llm(system_prompt,text):
    key = os.getenv("DASHSCOPE_API_KEY")
    messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content":text}
        ]
    try:
        response=Generation.call(
            model="qwen-max",
            messages=messages,
            temperature=0.1
        )
        # app/api/service/llm_service.py
        if response.status_code ==200:
            content=response.output.text
            match=re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                clean_content = match.group()
                try:
                    # 尝试标准解析
                    data = json.loads(clean_content)
                except json.JSONDecodeError:
                    # 如果失败，使用 json_repair 进行智能修复
                    fixed_json = repair_json(clean_content)
                    data = json.loads(fixed_json)
                return data
            else:
                raise InvalidJSON("未能找到合法的JSON数据")
    except LLMCalledFailed as e :
        raise LLMCalledFailed({e})

