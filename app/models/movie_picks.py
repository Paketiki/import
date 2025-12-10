# app/models/movie_picks.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base

class MoviePick(Base):
    __tablename__ = "movie_picks"
    
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    pick_id = Column(Integer, ForeignKey("picks.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())