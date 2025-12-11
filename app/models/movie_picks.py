from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class MoviePick(Base):
    __tablename__ = "movie_picks"
    
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    pick_id = Column(Integer, ForeignKey("picks.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    movie = relationship("Movie", back_populates="picks")
    pick = relationship("Pick", back_populates="movies")
