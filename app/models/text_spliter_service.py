from typing import Optional

from pydantic import BaseModel

class BaseInfo(BaseModel):
    name:str |None=None
    phone:str |None=None
    email:str |None=None
    gender:str |None=None
    age:int |None=None
    city:str |None=None

class Skills(BaseModel):
    programming:list[str]|None=None
    frameworks:list[str]|None=None
    databases:list[str]|None=None
    middleware:list[str]|None=None
    tools:list[str]|None=None

class EducationData(BaseModel):
    school:str|None=None
    major:str|None=None
    degree:str|None=None
    startTime:str|None=None
    endTime:str|None=None
    gpa:str|None=None
    rank:str|None=None
class ResumeText(BaseModel):
    baseInfo:Optional[BaseInfo]=None
    skills:Optional[Skills]=None
    education:list[EducationData] |None=None
    awards:str|None=None
    overallSummary:str|None=None
    workExperience:str|None=None
    projectExperience:str|None=None
class Data(BaseModel):
    resumeText:Optional[ResumeText]=None
    resumeId: str