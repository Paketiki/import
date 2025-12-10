from .enums import UserRole
from .users import UserBase, UserCreate, UserUpdate, UserInDB, User, SUserGet
from .movies import MovieBase, MovieCreate, MovieUpdate, MovieInDB, MovieWithPicks, Movie, MovieResponse, MovieFilters
from .auth import Token, TokenData, LoginRequest
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
    "Movie", "MovieResponse", "MovieFilters",
    
    # Reviews
    "ReviewBase", "ReviewCreate", "ReviewUpdate", "ReviewInDB", "ReviewWithDetails", 
    "Review", "ReviewResponse",
    
    # Picks
    "PickBase", "PickCreate", "PickInDB", "Pick",
    
    # Auth
    "Token", "TokenData", "LoginRequest",
    
    # New schemas
    "MovieStatBase", "MovieStatCreate", "MovieStatUpdate", "MovieStat", "MovieStatWithMovie",
    "RoleBase", "RoleCreate", "RoleUpdate", "Role", "RoleInDB",
    "MoviePickBase", "MoviePickCreate", "MoviePickUpdate", "MoviePick", "MoviePickWithDetails",
    "SRoleGetWithRels", "SUserGetWithRels"
]