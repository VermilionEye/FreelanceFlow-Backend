from sqlalchemy import create_engine
from app.models.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.role import Role
from app.models.time_entry import TimeEntry

# Создаем подключение к базе данных
DATABASE_URL = "postgresql+psycopg2://postgres:123321@localhost:5432/freelanceflow"
engine = create_engine(DATABASE_URL)

def init_db():
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("База данных успешно создана!") 