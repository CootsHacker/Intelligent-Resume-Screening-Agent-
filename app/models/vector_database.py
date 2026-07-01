from typing import Optional

from pydantic import BaseModel
class VectorData(BaseModel):
    resumeId: str
    overallSummary: str | None = None
    workExperience: str | None = None
    projectExperience: str | None = None
