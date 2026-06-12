# sigen-backend/auth/router.py
"""Endpoints de Autenticación."""
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from config import get_settings
from models.database import User, get_session
from auth.models import Token, UserCreate, UserRead
from auth.service import authenticate_user, create_access_token, get_current_active_user, get_current_admin_user, create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    s = get_settings()
    access_token_expires = timedelta(minutes=s.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserRead)
async def register_user(
    user_in: UserCreate, 
    session: Session = Depends(get_session)
    # En producción esto debería estar protegido (solo admin puede crear usuarios)
    # current_user: User = Depends(get_current_admin_user)
):
    return create_user(session, user_in)

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=List[UserRead])
async def read_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    users = session.exec(select(User)).all()
    return users
