"""
app/models.py – SQLModel data models
Roles mirror At The Helm: anonymous / member (≈user) / admin
"""

import uuid as _uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Role(str, Enum):
    anonymous = "anonymous"
    member = "member"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(_uuid.uuid4()),
        primary_key=True,
    )
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    password_hash: str = Field(...)
    role: str = Field(default=Role.member.value)
    display_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default=None)
