# app/models/movies.py
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer)
    rating = Column(Float)
    genre = Column(String)
    poster_url = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Используем строки для ленивой загрузки
    user = relationship("User", back_populates="movies", foreign_keys=[created_by])
    
    picks = relationship(
        "Pick", 
        secondary="movie_picks", 
        back_populates="movies",
        lazy="dynamic",
        overlaps="movie_picks"
    )
    
    movie_picks = relationship(
        "MoviePick", 
        back_populates="movie",
        lazy="dynamic",
        overlaps="picks"
    )