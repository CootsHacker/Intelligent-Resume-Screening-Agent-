from pydantic import BaseModel
"""
向量存储请求体={
{
  "resumeId": "res_2001",
  "resumeText":{
      "baseInf":"此部分包含个人基本信息：姓名，电话，邮箱地址，大学，专业，毕业时间",
      "skills":"此部分按照最初提取机构中的不变",
      "projects":"此部分把项目全部塞进去，解包",
      "workExperience":"此部分就是原本的结构化提取数据"
  }
}
"""
class Info(BaseModel):
    baseInfo:str
    skills:str
    projects:str
    workExperience:str

class TextSpliter(BaseModel):
    resumeId:str |None=None
    resumeText:Info
