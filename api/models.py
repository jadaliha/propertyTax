from sqlmodel import Field, SQLModel, Column, String, text
from datetime import datetime
from typing import Annotated, Set
from pydantic import EmailStr, HttpUrl, BaseModel
from enum import Enum
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
from uuid import UUID

def PK():
    return Annotated[UUID,                  Field(default=None, sa_column=Column(postgresql.UUID,server_default=text("uuid_generate_v4()"), primary_key=True))]

Now     = Annotated[datetime,               Field(default=datetime.now())]
UID     = Annotated[UUID,                   Field(foreign_key="user.id")]
def vector(): 
    return Annotated[list[float],           Field(sa_column=Column(Vector(384)))] 


def tags():
    return Annotated[Set[str],              Field(default=None, sa_column=Column(postgresql.ARRAY(String)))]
def FK(table):
    return Annotated[UUID,                  Field(foreign_key=f"{table}.id")]

class Role(str, Enum):
    admin       = "admin"
    user        =  "user"
    assistant   = "assistant"

class User(SQLModel, table=True):
    id      : PK()
    fullname: str
    email   : Annotated[str, EmailStr] = Field(index=True)
    address : str
    role    : Role = Role.user
    photo   : Annotated[str, HttpUrl]
    phonenumer: str
    


class Document(SQLModel, table=True):
    id      : PK()
    name    : str = Field(index=True,       description="The name of the file.")
    size    : int = Field(gt=0, default=0,  description="The file size in bytes.")
    type    : str = Field(default=None,     description="The media type of the file.")
    url     : str = Field(default="",       description="The URL to download the file.")
    storage_object_id   : str  = Field(index=True)   
    is_favorited        : bool = Field(default=False, description="Is the document favorited?")
    created_by          : UID
    created_at          : Now
    modified_at         : Now
    # preview             : str = ""
    # summary             : str = ""
    # disabled            : bool = False
    # owner: Users | None = Relationship(back_populates="users")
    