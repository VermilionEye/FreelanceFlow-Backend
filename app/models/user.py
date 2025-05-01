from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

# Association table for User-Role relationship
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    profile_picture = Column(String, nullable=True)
    hourly_rate = Column(Float, default=0.0)
    verification_token = Column(String, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=user_role, back_populates="users")
    projects = relationship("Project", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    time_entries = relationship("TimeEntry", back_populates="user") 