from pydantic import BaseModel

class AuthorDTO(BaseModel):
    uuid: str
    name: str
