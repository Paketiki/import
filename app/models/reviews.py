# app/models/reviews.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    text = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    author_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())