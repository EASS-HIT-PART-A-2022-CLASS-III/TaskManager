from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserShow(UserBase):
    id: int

    class Config:
        orm_mode = True
