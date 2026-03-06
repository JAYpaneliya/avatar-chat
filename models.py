from pydantic import BaseModel
from typing import Optional


class AvatarCreate(BaseModel):
    name: str
    age: Optional[int] = None
    location: Optional[str] = None
    relationship: str
    situation: Optional[str] = None
    occupation: Optional[str] = None
    interests: Optional[str] = None
    behaviour: Optional[str] = None
    communication_style: str
    slangs: Optional[str] = None
    language: Optional[str] = "English"


class ChatRequest(BaseModel):
    user_id: str
    avatar_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    avatar_name: str


class MessageHistory(BaseModel):
    role: str
    content: str