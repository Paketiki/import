from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.schemas.enums import UserRole  # Импортируем из схем

class User(Base):
    __tablename__ = "users"
    
    username = Column(String(50), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default=UserRole.VIEWER.value)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")