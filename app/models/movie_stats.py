from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class MovieStat(Base):
    __tablename__ = "movie_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), unique=True, nullable=False)
    views_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    picks_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    movie = relationship("Movie", back_populates="stat")