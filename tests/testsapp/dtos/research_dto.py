from pydantic import BaseModel


class ResearchDTO(BaseModel):
    uuid: str
    name: str
    is_public: bool
