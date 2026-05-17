from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str


class MessageResponse(BaseModel):
    message: str


class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class NoteUpdate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShareNoteRequest(BaseModel):
    share_with_email: EmailStr


class ActionItemsResponse(BaseModel):
    note_id: int
    action_items: list[str]