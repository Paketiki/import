from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    overview = Column(Text)  # Краткое описание
    year = Column(Integer, index=True)
    duration = Column(Integer)  # в минутах
    director = Column(String(255))
    rating = Column(Float, default=0.0, index=True)
    age_rating = Column(String(10))
    poster_url = Column(String(500))
    genre = Column(String(100), index=True)
    created_by = Column(Integer, ForeignKey('users.id'))  # Кто создал фильм
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    
    # Связь с подборками через промежуточную таблицу movie_picks
    picks = relationship(
        "Pick", 
        secondary="movie_picks",
        back_populates="movies",
        lazy="selectin"
    )
    
    # Связь с пользователями, добавившими фильм в избранное
    favorited_by = relationship(
        "User",
        secondary="user_favorite_movies",
        back_populates="favorite_movies",
        lazy="selectin"
    )
    
    # Связь с создателем фильма
    creator = relationship("User", back_populates="created_movies", foreign_keys=[created_by])
    
    # Связь со статистикой
    stat = relationship("MovieStat", back_populates="movie", uselist=False, cascade="all, delete-orphan")