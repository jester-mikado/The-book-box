from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class BookCreate(BaseModel):

    title: str
    author: str
    genre: str
    summary: str


class ReviewCreate(BaseModel):
    rating: int
    comment: str


class Token(BaseModel):
    access_token: str
    token_type: str