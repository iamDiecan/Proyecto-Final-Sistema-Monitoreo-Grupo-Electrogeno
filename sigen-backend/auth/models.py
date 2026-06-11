# sigen-backend/auth/models.py
"""Esquemas Pydantic para Autenticación."""
from pydantic import BaseModel
from typing import Optional
from models.database import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""
    full_name: Optional[str] = ""
    role: Optional[UserRole] = UserRole.TECNICO

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
