from .enums import UserRole
from .users import UserBase, UserCreate, UserUpdate, UserInDB, User, SUserGet
from .movies import MovieBase, MovieCreate, MovieUpdate, MovieInDB, MovieWithPicks, Movie, MovieResponse, MovieFilters, MovieListResponse
from .reviews import ReviewBase, ReviewCreate, ReviewUpdate, ReviewInDB, ReviewWithDetails, Review, ReviewResponse
from .picks import PickBase, PickCreate, PickInDB, Pick
from .auth import Token, TokenData, LoginRequest, PaginatedResponse
from .movie_stats import MovieStatBase, MovieStatCreate, MovieStatUpdate, MovieStat, MovieStatWithMovie
from .roles import RoleBase, RoleCreate, RoleUpdate, Role, RoleInDB
from .movie_picks import MoviePickBase, MoviePickCreate, MoviePickUpdate, MoviePick, MoviePickWithDetails
from .relations_users_roles import SRoleGetWithRels, SUserGetWithRels

__all__ = [
    # Enums
    "UserRole",
    
    # Users
    "UserBase", "UserCreate", "UserUpdate", "UserInDB", "User", "SUserGet",
    
    # Movies
    "MovieBase", "MovieCreate", "MovieUpdate", "MovieInDB", "MovieWithPicks", 
    "Movie", "MovieResponse", "MovieFilters", "MovieListResponse",
    
    # Reviews
    "ReviewBase", "ReviewCreate", "ReviewUpdate", "ReviewInDB", "ReviewWithDetails", 
    "Review", "ReviewResponse",
    
    # Picks
    "PickBase", "PickCreate", "PickInDB", "Pick",
    
    # Auth
    "Token", "TokenData", "LoginRequest",
    
    # Common
    "PaginatedResponse",
    
    # New schemas
    "MovieStatBase", "MovieStatCreate", "MovieStatUpdate", "MovieStat", "MovieStatWithMovie",
    "RoleBase", "RoleCreate", "RoleUpdate", "Role", "RoleInDB",
    "MoviePickBase", "MoviePickCreate", "MoviePickUpdate", "MoviePick", "MoviePickWithDetails",
    "SRoleGetWithRels", "SUserGetWithRels"
]