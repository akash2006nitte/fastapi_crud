from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    bio: str | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PostCreate(BaseModel):
    user_id: int
    image_url: str
    caption: str | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_url: str
    caption: str | None = None
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    user_id: int
    text: str


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime