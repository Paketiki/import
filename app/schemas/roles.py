from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemas.users import SUserGet


class SRoleAdd(BaseModel):
    name: str


class SRoleGet(BaseModel):
    id: int
