from pydantic import BaseModel


class ResumeRequest(BaseModel):#接收/api/v1/resume/parse JSON格式数据
    resumeId: str | None = None
    filePath: str
    fileName: str | None = None
    fileType: str | None = None