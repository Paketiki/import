from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Pick(Base):
    __tablename__ = "picks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    # optional creator of the pick
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    movies = relationship("Movie", secondary="movie_picks", back_populates="picks")
    creator = relationship("User", back_populates="picks")