from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_time: Optional[datetime]
    estimated_hours: Optional[float]

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 