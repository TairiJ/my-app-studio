"""
app/security/rbac.py
Role-based access control — ported from At The Helm's middleware/rbac.ts

Role hierarchy:  anonymous(0) < member(1) < admin(2)
"""

from fastapi import Depends, HTTPException, status

from app.models import Role, User
from app.security.auth import get_current_user

ROLE_HIERARCHY: dict[str, int] = {
    Role.anonymous: 0,
    Role.member: 1,
    Role.admin: 2,
}


def require_role(*allowed: str):
    """
    Dependency factory — raises 403 if the authenticated user's role
    is below the minimum allowed level.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    min_level = min(ROLE_HIERARCHY.get(r, 0) for r in allowed)

    def checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {', '.join(allowed)}",
            )
        return current_user

    return checker
