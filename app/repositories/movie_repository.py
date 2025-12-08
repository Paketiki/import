from sqlalchemy.orm import Session
from app.models.movies import Movie

class MovieRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_movie(self, movie_data: dict):
        db_movie = Movie(**movie_data)
        self.db.add(db_movie)
        self.db.commit()
        self.db.refresh(db_movie)
        return db_movie
    
    def get_movie_by_title(self, title: str):
        return self.db.query(Movie).filter(Movie.title == title).first()
    
    def bulk_create_movies(self, movies_data: list[dict]):
        movies = [Movie(**data) for data in movies_data]
        self.db.add_all(movies)
        self.db.commit()
        return movies