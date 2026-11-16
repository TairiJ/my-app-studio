"""
tests/test_app.py – Full checks for APP-001, APP-002, APP-003
Run:  pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import Role, User
from app.security.auth import hash_password

# ── Test DB setup ─────────────────────────────────────────────────────────────

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, raise_server_exceptions=True)
    yield client
    app.dependency_overrides.clear()


# ── APP-001: Branded homepage ─────────────────────────────────────────────────

class TestHomepage:
    def test_homepage_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_homepage_contains_brand_name(self, client):
        response = client.get("/")
        assert "At The Helm" in response.text

    def test_homepage_contains_tagline(self, client):
        response = client.get("/")
        assert "Cockpit" in response.text or "Orchestration" in response.text

    def test_homepage_contains_archetype(self, client):
        response = client.get("/")
        assert "Commander" in response.text

    def test_homepage_contains_cta_links(self, client):
        response = client.get("/")
        assert "/auth/signup-page" in response.text
        assert "/auth/login-page" in response.text


# ── APP-002: Signup / Login / Dashboard / Logout ──────────────────────────────

class TestAuth:
    def test_signup_creates_user(self, client):
        res = client.post("/auth/signup", json={
            "username": "testpilot", "password": "secure123"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["user"]["username"] == "testpilot"
        assert data["user"]["role"] == "member"
        assert "token" in data

    def test_signup_duplicate_username_fails(self, client):
        client.post("/auth/signup", json={"username": "testpilot2", "password": "pass123"})
        res = client.post("/auth/signup", json={"username": "testpilot2", "password": "other123"})
        assert res.status_code == 409

    def test_signup_short_password_fails(self, client):
        res = client.post("/auth/signup", json={"username": "abc", "password": "12"})
        assert res.status_code == 400

    def test_login_valid_credentials(self, client):
        client.post("/auth/signup", json={"username": "logintest", "password": "mypassword"})
        res = client.post("/auth/login", json={"username": "logintest", "password": "mypassword"})
        assert res.status_code == 200
        assert "token" in res.json()

    def test_login_wrong_password_fails(self, client):
        client.post("/auth/signup", json={"username": "pilotX", "password": "rightpass"})
        res = client.post("/auth/login", json={"username": "pilotX", "password": "wrongpass"})
        assert res.status_code == 401

    def test_dashboard_requires_auth(self, client):
        res = client.get("/dashboard")
        # Without a token the dependency raises 401
        assert res.status_code == 401

    def test_dashboard_accessible_with_token(self, client):
        signup = client.post("/auth/signup", json={"username": "dashtest", "password": "password1"})
        token = signup.json()["token"]
        res = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "dashtest" in res.text

    def test_me_returns_user(self, client):
        signup = client.post("/auth/signup", json={"username": "metest", "password": "password1"})
        token = signup.json()["token"]
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["user"]["username"] == "metest"

    def test_me_no_token_returns_anonymous(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 200
        assert res.json()["user"] is None


# ── APP-003: Role enforcement ─────────────────────────────────────────────────

class TestRBAC:
    def _make_admin(self, session: Session, username: str, password: str) -> str:
        """Helper: create a user, set role=admin, return token."""
        import uuid

        from app.security.auth import create_access_token
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=hash_password(password),
            role=Role.admin,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return create_access_token({"sub": user.id, "role": user.role})

    def test_admin_panel_blocked_for_anonymous(self, client):
        res = client.get("/admin")
        assert res.status_code == 401

    def test_admin_panel_blocked_for_member(self, client):
        signup = client.post("/auth/signup", json={"username": "memberonly", "password": "pass123"})
        token = signup.json()["token"]
        res = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403

    def test_admin_panel_accessible_for_admin(self, client, session):
        token = self._make_admin(session, "superadmin", "adminpass")
        res = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "Admin Panel" in res.text

    def test_member_cannot_see_other_users(self, client):
        signup = client.post("/auth/signup", json={"username": "normalmember", "password": "pass123"})
        token = signup.json()["token"]
        res = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        # Must be forbidden, not 200
        assert res.status_code == 403
