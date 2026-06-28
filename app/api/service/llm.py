import json
import os
import re

from dashscope import Generation

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
                data = json.loads(clean_content)
                return data
            else:
                raise InvalidJSON("未能找到合法的JSON数据")
    except LLMCalledFailed as e :
        raise LLMCalledFailed({e})

