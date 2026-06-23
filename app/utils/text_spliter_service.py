"""
向量存储请求体={
{
  "resumeId": "res_2001",
  "resumeText":{
      "baseInf":"此部分包含个人基本信息：姓名，电话，邮箱地址，大学，专业，毕业时间",
      "skills":"此部分按照最初提取机构中的不变",
      "projects":"此部分把项目全部塞进去，解包",
      "workExperience":"此部分就是原本的结构化提取数据"
      "awards":""
      "overallSummary":""
  }
}
"""
from app.models.text_spliter_service import ResumeText


#此模块为分类处理传入数据

def text_input(request_data:ResumeText):
    baseInfo_dict=request_data.baseInfo.model_dump()
    skills_dict=request_data.skills.model_dump()
    education_dict=request_data.education.model_dump()
    projects_text=request_data.projects
    awards_text=request_data.awards
    overallSummary_text=request_data.overallSummary
    workExperience_text=request_data.workExperience
    resumeId=request_data.resumId
    return baseInfo_dict , skills_dict,education_dict,projects_text,awards_text,overallSummary_text,workExperience_text,resumeId