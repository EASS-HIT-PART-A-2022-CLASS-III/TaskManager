from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class TaskStatus(str,Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class TaskCreate(BaseModel):

    title: str
    description: str | None = None
    status: TaskStatus | None = TaskStatus.IN_PROGRESS
    deadline: datetime | None = None
    
    
class TaskShow(TaskCreate):
    id: int
    project_id: int
    created_by_id: int
    assignee_id: int | None = None
    date_of_creation: datetime
    
    class Config:
        orm_mode = True


class TaskUpdate(BaseModel):

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    deadline: datetime | None = None
    assignee_id: int | None = None