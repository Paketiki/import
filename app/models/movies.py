from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    rating = Column(Float, nullable=False, index=True)  # Изменено с DECIMAL на Float для SQLite
    poster = Column(String(500))
    overview = Column(Text)
    review = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    picks = relationship("Pick", secondary="movie_picks", back_populates="movies")
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")

class MoviePick(Base):
    __tablename__ = "movie_picks"
    
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    pick_id = Column(Integer, ForeignKey("picks.id", ondelete="CASCADE"), primary_key=True)