from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class Pick(Base):
    __tablename__ = "picks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    movies = relationship(
        "Movie", 
        secondary="movie_picks", 
        back_populates="picks",
        overlaps="movie_picks"
    )
    
    movie_picks = relationship(
        "MoviePick", 
        back_populates="pick",
        overlaps="movies"
    )

    
    # Создатель подборки (необязательное поле)
    creator = relationship("User", back_populates="created_picks", foreign_keys=[created_by])