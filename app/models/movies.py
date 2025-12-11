from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, DateTime, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database.base import Base  # Импортируем Base из base.py

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    overview = Column(String, nullable=True)
    year = Column(Integer)
    genre = Column(String, nullable=False, index=True)
    rating = Column(Float, default=0.0)
    poster_url = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    creator = relationship("User", foreign_keys=[created_by])
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="movie", cascade="all, delete-orphan")
    picks = relationship("MoviePick", back_populates="movie", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"
