"""
app/routers/auth.py  –  APP-002: Signup, login, logout
Ported from At The Helm's routes/auth.ts
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.models import Role, User
from app.security.auth import (
    create_access_token,
    get_current_user_optional,
    hash_password,
    verify_password,
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SignupForm(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None


class LoginForm(BaseModel):
    username: str
    password: str


# ── API endpoints (JSON) ──────────────────────────────────────────────────────

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(form: SignupForm, session: Session = Depends(get_session)):
    if len(form.username) < 3 or len(form.password) < 6:
        raise HTTPException(400, "Username ≥ 3 chars, password ≥ 6 chars")

    existing = session.exec(select(User).where(User.username == form.username)).first()
    if existing:
        raise HTTPException(409, "Username already taken")

    user = User(
        id=str(uuid.uuid4()),
        username=form.username,
        password_hash=hash_password(form.password),
        role=Role.member,
        display_name=form.display_name or form.username,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"user": {"id": user.id, "username": user.username, "role": user.role}, "token": token}


@router.post("/login")
def login(form: LoginForm, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    session.commit()

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"user": {"id": user.id, "username": user.username, "role": user.role}, "token": token}


@router.get("/me")
def me(current_user: User = Depends(get_current_user_optional)):
    if current_user is None:
        return {"user": None, "role": "anonymous"}
    return {"user": {"id": current_user.id, "username": current_user.username, "role": current_user.role}}


# ── HTML page routes ──────────────────────────────────────────────────────────

@router.get("/signup-page", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login-page", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
