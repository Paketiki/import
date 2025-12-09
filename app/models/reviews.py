from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base 

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    author = Column(String(100), nullable=False)  # Имя автора (может отличаться от username)
    role = Column(String(50), nullable=False)  # Роль автора (Зритель, Критик и т.д.)
    rating = Column(Float, nullable=False)  # Оценка от 0 до 10
    text = Column(Text, nullable=False)  # Текст рецензии
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Связи
    movie = relationship("Movie", back_populates="reviews")
    user = relationship("User", back_populates="reviews")