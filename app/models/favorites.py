from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    user = relationship("User", backref="favorites")
    movie = relationship("Movie", backref="favorited_by")
    
    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, movie_id={self.movie_id})>"
