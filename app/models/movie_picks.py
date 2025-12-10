from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class MoviePick(Base):
    __tablename__ = "movie_picks"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    pick_id = Column(Integer, ForeignKey("picks.id"))
    
    movie = relationship(
        "Movie", 
        back_populates="movie_picks",
        overlaps="picks"
    )
    
    pick = relationship(
        "Pick", 
        back_populates="movie_picks",
        overlaps="movies"
    )