from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base 

# Промежуточная таблица для избранных фильмов
user_favorite_movies = Table(
    'user_favorite_movies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, server_default=func.now())
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_native = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    role = relationship("Role", back_populates="users")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    # Связь с фильмами через промежуточную таблицу
    favorite_movies = relationship(
        "Movie",
        secondary=user_favorite_movies,
        back_populates="favorited_by",
        lazy="selectin"
    )
    
    # Связь с созданными фильмами
    created_movies = relationship("Movie", back_populates="creator", foreign_keys="Movie.created_by")
    
    # Связь с подборками, которые создал пользователь
    created_picks = relationship("Pick", back_populates="creator", foreign_keys="Pick.created_by")