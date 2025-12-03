from enum import Enum

class UserRole(str, Enum):
    VIEWER = "viewer"
    ADMIN = "admin"