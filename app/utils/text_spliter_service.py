import json

from app.models.text_spliter_service import Data
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.vector_database import VectorData


#切分长文本
def text_splitter(text)->list:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,  # 每个文本块最大长度（建议设置为 100~150 汉字，契合你的模型最佳长度）
        chunk_overlap=15,  # 文本块之间的重叠长度（保留上下文，避免语义断裂）
        separators=["\n\n", "\n", "。","！", "？","；","，"]  # 优先按段落、换行、中文句号等标点切分
    )
    #二次文本切分
    text_splitter_2=RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=15,
        separators=["。","：","，"]
    )
    text=text_splitter.split_text(text)
    text_chunk=[]
    for chunk in text:
        if len(chunk)>150:
            temp=text_splitter_2.split_text(chunk)
            if isinstance(temp, list):
                text_chunk.extend(temp)
            else:
                text_chunk.append(temp)
        else:
            text_chunk.append(chunk)
    return text_chunk
#此模块为分类处理传入数据
def text_input(request_data:VectorData):
    resumeId=request_data.resumeId
    projects=request_data.projectExperience
    workExperience=request_data.workExperience
    overallSummary=request_data.overallSummary

    projects_chunk=text_splitter(projects)
    workExperience_chunk=text_splitter(workExperience)
    overallSummary_chunk=text_splitter(overallSummary)

    return resumeId,workExperience_chunk,overallSummary_chunk,projects_chunk