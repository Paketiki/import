# app/models/users.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ВРЕМЕННО УДАЛИТЕ ВСЕ ОТНОШЕНИЯ
    # Они будут добавлены позже через configure_mappers()