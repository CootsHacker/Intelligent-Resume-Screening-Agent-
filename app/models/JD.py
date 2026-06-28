from pydantic import BaseModel


class JDRequests(BaseModel):
    jdId:str
    jdTitle:str |None=None
    jdContent:str |None=None
