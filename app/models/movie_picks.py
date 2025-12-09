from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class MoviePick(Base):
    __tablename__ = "movie_picks"
    
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True)
    pick_id = Column(Integer, ForeignKey('picks.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    
    # Опционально: связи для быстрого доступа
    movie = relationship("Movie", lazy="selectin")
    pick = relationship("Pick", lazy="selectin")
    
    # Определяем составной первичный ключ
    __table_args__ = (
        PrimaryKeyConstraint('movie_id', 'pick_id'),
    )