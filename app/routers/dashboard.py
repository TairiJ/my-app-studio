"""
app/routers/dashboard.py  –  APP-002: Private dashboard + APP-003: Admin panel
Server-enforced roles via RBAC dependency.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.security.auth import get_current_user
from app.security.rbac import require_role

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),   # 401 if not logged in
):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": current_user},
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    current_user: User = Depends(require_role("admin")),   # 403 if not admin
    session: Session = Depends(get_session),
):
    users = session.exec(select(User)).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "user": current_user, "users": users},
    )
