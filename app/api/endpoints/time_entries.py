from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.base import get_db
from app.models.time_entry import TimeEntry
from app.schemas.time_entry import TimeEntryCreate, TimeEntry as TimeEntrySchema
from app.core.dependencies import get_current_active_user

router = APIRouter(tags=["time-entries"])

@router.post("/tasks/{task_id}/time", response_model=TimeEntrySchema)
async def create_time_entry(
    task_id: int,
    time_entry: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    db_time_entry = TimeEntry(
        **time_entry.dict(),
        task_id=task_id,
        user_id=current_user.id
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

@router.get("/tasks/{task_id}/time", response_model=List[TimeEntrySchema])
async def read_task_time_entries(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    time_entries = db.query(TimeEntry).filter(
        TimeEntry.task_id == task_id,
        TimeEntry.user_id == current_user.id
    ).all()
    return time_entries

@router.delete("/tasks/{task_id}/time/{time_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    task_id: int,
    time_entry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    time_entry = db.query(TimeEntry).filter(
        TimeEntry.id == time_entry_id,
        TimeEntry.task_id == task_id,
        TimeEntry.user_id == current_user.id
    ).first()
    if time_entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    db.delete(time_entry)
    db.commit()
    return {"ok": True}

@router.get("/users/{user_id}/time-statistics")
async def get_user_time_statistics(
    user_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view other user's time statistics"
        )
    
    query = db.query(TimeEntry).filter(TimeEntry.user_id == user_id)
    
    if start_date:
        query = query.filter(TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.end_time <= end_date)
    
    time_entries = query.all()
    
    total_time = sum(entry.duration for entry in time_entries)
    billable_time = sum(entry.duration for entry in time_entries if entry.is_billable)
    
    return {
        "total_time": total_time,
        "billable_time": billable_time,
        "number_of_entries": len(time_entries)
    } 