from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserList(BaseModel):
    id: int
    username: str
    email: EmailStr

    # password: str
    model_config = ConfigDict(from_attributes=True)


class UserRetrieve(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    id: int
    username: str
    email: EmailStr
    # password: str


class UserLogin(BaseModel):
    username: str
    password: str
