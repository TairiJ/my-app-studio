# ⚓ At The Helm – App Studio

**IS373 App Studio** | APP-001 · APP-002 · APP-003

A branded FastAPI web application with authentication and role-based access control, built on the **At The Helm** brand. Part of the IS373 App Studio assignment.

## Features
- **APP-001** – Branded homepage (⚓ At The Helm, The Commander archetype)
- **APP-002** – Signup, login, private dashboard, and logout via JWT auth
- **APP-003** – Member/admin role enforcement on the server; roles managed via local CLI

## Quick Start

```bash
# 1. Clone
git clone git@github.com:YOUR-USERNAME/my-app-studio.git
cd my-app-studio

# 2. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
uvicorn app.main:app --reload
```

Open **http://localhost:8000** in your browser.

## Running Tests

```bash
pytest tests/ -v
```

## Role Management CLI

```bash
# List all users
python -m app.cli list-users

# Promote a user to admin
python -m app.cli promote <username> admin

# Demote back to member
python -m app.cli promote <username> member
```

## Project Structure

```
app/
├── main.py          # FastAPI app + router registration
├── models.py        # SQLModel User model (roles: anonymous/member/admin)
├── database.py      # SQLite engine
├── cli.py           # Trusted local CLI for role management
├── routers/
│   ├── home.py      # GET /           (APP-001)
│   ├── auth.py      # POST /auth/signup, /auth/login (APP-002)
│   └── dashboard.py # GET /dashboard, /admin        (APP-002/003)
├── security/
│   ├── auth.py      # JWT helpers (ported from At The Helm)
│   └── rbac.py      # require_role() dependency factory
├── templates/       # Jinja2 HTML templates
└── static/brand/    # CSS + brand assets
tests/
└── test_app.py      # Full checks for all three lessons
.github/workflows/
└── ci.yml           # Lint + test CI jobs
```

## See Also
- [SPEC.md](SPEC.md) – Decisions, implementation links, and check evidence
- [LEARNING.md](LEARNING.md) – Personal reflections and observations
