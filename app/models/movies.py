from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    release_year = Column(Integer)
    genre = Column(String(100))
    duration = Column(Integer)
    rating = Column(Float)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    creator = relationship("User", back_populates="movies")
    stat = relationship("MovieStat", back_populates="movie", uselist=False)
    movie_picks = relationship("MoviePick", back_populates="movie")
    # direct many-to-many access to picks through association table
    picks = relationship("Pick", secondary="movie_picks", back_populates="movies")
    reviews = relationship("Review", back_populates="movie")


class MoviePick(Base):
    __tablename__ = 'movie_picks'
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    pick_id = Column(Integer, ForeignKey('picks.id'), nullable=False)
    added_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    movie = relationship("Movie")
    pick = relationship("Pick")
    user = relationship("User")