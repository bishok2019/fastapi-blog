from pydantic import BaseModel, EmailStr


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int


class PostList(BaseModel):
    title: str
    content: str
    author_id: int


class PostRetrieve(BaseModel):
    title: str
    content: str
    author_id: int


class PostUpdate(BaseModel):
    title: str
    content: str
    author_id: int
