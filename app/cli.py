"""
app/cli.py  –  Trusted local CLI for role management (APP-003)
Run:  python -m app.cli promote <username> admin
      python -m app.cli list-users
"""

import sys

from sqlmodel import Session, select

from app.database import engine, init_db
from app.models import Role, User


def get_session():
    return Session(engine)


def list_users():
    init_db()
    with get_session() as session:
        users = session.exec(select(User)).all()
        if not users:
            print("No users found.")
            return
        print(f"{'USERNAME':<20} {'ROLE':<12} {'EMAIL':<30} ID")
        print("-" * 80)
        for u in users:
            print(f"{u.username:<20} {u.role:<12} {u.email or '':<30} {u.id[:8]}…")


def promote(username: str, role: str):
    if role not in [r.value for r in Role]:
        print(f"❌  Invalid role '{role}'. Choose: anonymous, member, admin")
        sys.exit(1)
    init_db()
    with get_session() as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"❌  User '{username}' not found.")
            sys.exit(1)
        old_role = user.role
        user.role = role
        session.add(user)
        session.commit()
        print(f"✅  {username}: {old_role} → {role}")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python -m app.cli list-users")
        print("  python -m app.cli promote <username> <role>")
        sys.exit(0)

    cmd = args[0]
    if cmd == "list-users":
        list_users()
    elif cmd == "promote" and len(args) == 3:
        promote(args[1], args[2])
    else:
        print(f"Unknown command: {' '.join(args)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
