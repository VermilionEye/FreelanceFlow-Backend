from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.project import ProjectStatus

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime]
    status: ProjectStatus
    client_name: str
    budget: float

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    user_id: int
    total_tasks: int
    completed_tasks: int

    class Config:
        from_attributes = True 