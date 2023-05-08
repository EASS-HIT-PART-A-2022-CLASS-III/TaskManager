from pydantic import BaseModel
from schemas.user_schema import UserShow

class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    

class ProjectCreate(ProjectBase):
    pass

class ProjectShow(ProjectBase):
    creator_id: int
    users: list[UserShow] = []
    managers: list[UserShow] = []
    class Config:
        orm_mode = True