"""
app/routers/home.py  –  APP-001: Branded homepage
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "brand": {
                "name": "At The Helm",
                "tagline": "The AI Operator Cockpit for Centralized Orchestration & Governance.",
                "archetype": "The Commander",
                "promise": "Total visibility and control over your AI fleet — one dashboard, every agent.",
            },
        },
    )
