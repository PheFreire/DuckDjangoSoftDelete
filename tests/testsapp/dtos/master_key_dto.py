from pydantic import BaseModel

class MKDTO(BaseModel):
    uuid: str
    name: str
