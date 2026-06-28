import json
import os
import re
import time
from typing import Any

import dashscope
from dashscope import Generation
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from starlette.responses import JSONResponse


app = FastAPI(title="Resume Deep Score Agent")


class ScoreAgentError(Exception):
    code = 5000

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class LLMCalledFailed(ScoreAgentError):
    code = 1002


class InvalidJSON(ScoreAgentError):
    code = 1004


class InvalidRequest(ScoreAgentError):
    code = 1006


class DeepScoreRequest(BaseModel):
    resumeId: str | None = None
    jobDescription: str | None = None
    resume: dict[str, Any] = Field(default_factory=dict)

    @field_validator("resume")
    @classmethod
    def validate_resume(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict) or not value:
            raise ValueError("resume must be a non-empty object")
        return value


SCORING_SYSTEM_PROMPT = """
你是一个专业的技术招聘 AI 助手，负责对本科应届生程序员的结构化简历进行深度打分。
请严格依据以下 10 分制标准评分，分数精确到小数点后一位，并只输出合法 JSON，不要输出 Markdown 或额外解释。

评分标准：
1. 教育经历，满分 1.5 分。
- 院校与专业背景，0.8 分：985/211 或双一流计算机相关专业 0.8 分；普通本科计算机相关专业 0.5 分；非计算机相关专业但自学转行 0.2 分。
- 学业表现与核心课程，0.7 分：GPA 排名前 20% 或国家级/校级奖学金 0.7 分；GPA 中等且核心课程成绩良好 0.4 分；成绩平平或核心课程缺失 0-0.2 分。

2. 实践与项目经历，满分 4.5 分。
- 经历丰富度与优先级，1.5 分：2 段及以上大厂/知名互联网实习 1.5 分；1 段高质量实习 1.0 分；仅校内课程设计或普通项目 0.5 分。ACM、蓝桥杯等国家级学科竞赛获奖或优秀毕业设计可额外加 0.5 分，但该小项上限仍为 1.5 分。
- 内容量化与逻辑，1.5 分：严格采用 STAR 法则、描述清晰且有具体业务数据 1.5 分；有逻辑但缺乏数据支撑 0.8 分；只罗列技术名词或模糊套话 0-0.3 分。
- 角色与个人贡献，1.5 分：明确核心开发/负责人并能说明技术难点和个人产出 1.5 分；普通参与者但能说明负责模块 0.8 分；角色模糊、看不出产出 0 分。

3. 专业技能与证书，满分 1.5 分。
- 技术栈匹配度，1.0 分：熟练掌握岗位 JD 要求核心技术栈，技术名词规范 1.0 分；部分匹配或技术栈陈旧 0.5 分；完全不匹配 0 分。
- 证书含金量，0.5 分：软考中高级、华为 HCIA/HCIP、CET-6/雅思高分等 0.5 分；计算机二级等基础证书 0.2 分；无相关证书 0 分。

4. 综合素质能力，满分 2.5 分。
- 职业规划清晰度，0.8 分：求职意向明确，过往经历围绕岗位展开 0.8 分；意向模糊或经历杂乱 0-0.3 分。
- 底层能力展现，0.8 分：项目或开源贡献体现代码规范、系统设计、问题排查、持续学习 0.8 分；仅机械代码搬运 0-0.3 分。
- 差异化竞争优势，0.9 分：高 Star GitHub、技术博客、独立上线运营项目、AI 应用开发经验等，一项或多项 0.9 分；仅常规课程作业 0 分。

5. 简历规范与排版为附加扣分项，记为 format_penalty，通常为 0 或负数，总分不得低于 0。
- 超过 2 页、排版花哨杂乱、中英文/数字间无空格、错别字或语法错误，视严重程度每次扣 0.1-0.3 分。
- 与岗位无关冗余信息扣 0.2 分。

评级参考：
- 8.5-10.0 分：S 级，强烈推荐面试，核心候选人。
- 7.0-8.4 分：A 级，推荐面试，具备良好潜力。
- 5.5-6.9 分：B 级，待定/备选，需结合笔试或面试表现。
- 5.5 分以下：C 级，不推荐，简历缺乏核心竞争力。

输出 JSON 字段必须完全符合：
{
  "total_score": 8.6,
  "level": "S",
  "interview_recommendation": "强烈推荐面试",
  "scores": {
    "education": 1.3,
    "practice_and_projects": 4.0,
    "skills_and_certificates": 1.3,
    "comprehensive_quality": 2.0,
    "format_penalty": 0
  },
  "evaluation_details": {
    "education": "简短理由",
    "practice_and_projects": "简短理由",
    "skills_and_certificates": "简短理由",
    "comprehensive_quality": "简短理由",
    "format_penalty": "简短理由"
  },
  "suggestions": [
    {
      "target_dimension": "实践与项目经历",
      "action": "补充量化数据",
      "detail": "结合候选人实际经历给出具体、可执行的修改建议"
    }
  ]
}

要求：
- 基本信息不作为打分项。
- 有岗位 JD 时，技术栈匹配、职业规划、项目相关性必须围绕 JD 评分；没有 JD 时按本科应届程序员通用标准评分。
- suggestions 必须与扣分点强关联，按优先级排序，禁止“继续努力”“提高沟通能力”等空泛建议。
- 如果简历信息不足，要保守评分，并在理由中说明缺失信息。
"""


def build_error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "data": None,
            "timestamp": int(time.time() * 1000),
        },
    )


def normalize_score_result(result: dict[str, Any], resume_id: str | None) -> dict[str, Any]:
    try:
        total_score = round(float(result.get("total_score", 0)), 1)
    except (TypeError, ValueError):
        raise InvalidJSON("total_score must be a number")

    total_score = max(0.0, min(10.0, total_score))
    level = result.get("level") or infer_level(total_score)

    data = {
        "resumeId": resume_id,
        "total_score": total_score,
        "level": level,
        "interview_recommendation": result.get("interview_recommendation", ""),
        "scores": result.get("scores", {}),
        "evaluation_details": result.get("evaluation_details", {}),
        "suggestions": result.get("suggestions", []),
    }
    return data


def infer_level(total_score: float) -> str:
    if total_score >= 8.5:
        return "S"
    if total_score >= 7.0:
        return "A"
    if total_score >= 5.5:
        return "B"
    return "C"


def extract_json_object(content: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise InvalidJSON("模型返回内容中未找到合法 JSON 对象")
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as exc:
        raise InvalidJSON(f"模型返回 JSON 解析失败: {exc}") from exc
    if not isinstance(data, dict):
        raise InvalidJSON("模型返回 JSON 必须是对象")
    return data


def call_score_llm(request_data: DeepScoreRequest) -> dict[str, Any]:
    api_key = os.getenv("DASHSCOPE_API_KEY")
    # dashscope.api_key = api_key
    if not api_key:
        raise LLMCalledFailed("缺少环境变量 DASHSCOPE_API_KEY")

    user_payload = {
        "岗位JD": request_data.jobDescription or "未提供，请按本科应届程序员通用标准评分。",
        "候选人结构化简历": request_data.resume,
    }
    messages = [
        {"role": "system", "content": SCORING_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "请根据以下输入对候选人简历进行深度打分，并严格输出 JSON：\n"
            + json.dumps(user_payload, ensure_ascii=False),
        },
    ]

    response = Generation.call(model="qwen-max", messages=messages, temperature=0.1)
    if getattr(response, "status_code", None) != 200:
        message = getattr(response, "message", "DashScope API 调用失败")
        raise LLMCalledFailed(f"DashScope API 调用失败: {message}")

    content = getattr(getattr(response, "output", None), "text", None)
    if not content:
        raise InvalidJSON("模型返回内容为空")
    return extract_json_object(content)


@app.exception_handler(ScoreAgentError)
async def score_agent_error_handler(request: Request, exc: ScoreAgentError):
    return build_error_response(exc.code, exc.message)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return build_error_response(1006, str(exc))


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    message = first_error.get("msg", "请求结构不合法")
    return build_error_response(1006, message)


@app.post("/agent/api/v1/resume/deep-score")
async def deep_score(request_data: DeepScoreRequest):
    try:
        raw_result = call_score_llm(request_data)
        data = normalize_score_result(raw_result, request_data.resumeId)
    except ScoreAgentError:
        raise
    except Exception as exc:
        raise LLMCalledFailed(str(exc)) from exc

    return {
        "code": 0,
        "message": "success",
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
