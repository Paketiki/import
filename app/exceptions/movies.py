from .base import NotFoundError

class UserNotFoundError(NotFoundError):
    def __init__(self, username: str = None):
        detail = f"User {username} not found" if username else "User not found"
        super().__init__(detail=detail)

class MovieNotFoundError(NotFoundError):
    def __init__(self, movie_id: int = None):
        detail = f"Movie with ID {movie_id} not found" if movie_id else "Movie not found"
        super().__init__(detail=detail)

class ReviewNotFoundError(NotFoundError):
    def __init__(self, review_id: int = None):
        detail = f"Review with ID {review_id} not found" if review_id else "Review not found"
        super().__init__(detail=detail)

class PickNotFoundError(NotFoundError):
    def __init__(self, pick_id: int = None):
        detail = f"Pick with ID {pick_id} not found" if pick_id else "Pick not found"
        super().__init__(detail=detail)