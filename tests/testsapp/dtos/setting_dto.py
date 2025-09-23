from pydantic import BaseModel

class SettingDTO(BaseModel):
    uuid: str
    name: str
