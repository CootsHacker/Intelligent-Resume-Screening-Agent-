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

from app.models.text_spliter_service import TextSpliter


#此服务为文档分块服务
def text_spliter(request_data:TextSpliter)->list:
    text=[]
    clean_data=request_data.model_dump(exclude_none=True)
    for key , value in clean_data.items():
        temp=key + value
