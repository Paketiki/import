from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Pick(Base):
    __tablename__ = "picks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))  # Кто создал подборку
    created_at = Column(DateTime, default=func.now())
    
    # Связи
    movies = relationship(
        "Movie", 
        secondary="movie_picks",
        back_populates="picks",
        lazy="selectin"
    )
    
    creator = relationship("User", back_populates="created_picks", foreign_keys=[created_by])