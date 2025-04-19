from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TimeEntryBase(BaseModel):
    start_time: datetime
    end_time: datetime
    duration: float
    description: Optional[str] = None
    is_billable: bool = True

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntryUpdate(TimeEntryBase):
    pass

class TimeEntry(TimeEntryBase):
    id: int
    task_id: int
    user_id: int

    class Config:
        from_attributes = True 