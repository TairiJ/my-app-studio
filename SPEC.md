# SPEC.md – At The Helm App Studio
## IS373 App Studio · Lessons APP-001 → APP-003

---

## APP-001 · Branded Homepage

### Decisions
| Decision | Choice | Reason |
|----------|--------|--------|
| Brand name | **At The Helm** | Pre-existing brand from IS373 group project |
| Archetype | **The Commander** | Control-plane / operator positioning |
| Tagline | "The AI Operator Cockpit for Centralized Orchestration & Governance." | Directly carried from existing README |
| Promise | "Total visibility and control over your AI fleet — one dashboard, every agent." | Condensed from the original project scope |
| Framework | **FastAPI + Jinja2** | Required by the assignment |
| Styling | Custom dark CSS (cockpit theme) | Matches the existing At The Helm visual identity |

### Implementation
- Route: [`app/routers/home.py`](app/routers/home.py) — `GET /`
- Template: [`app/templates/home.html`](app/templates/home.html)
- CSS: [`app/static/brand/style.css`](app/static/brand/style.css)

### Check
- `GET /` returns `200 OK` with brand name, archetype, and CTA links — verified by `pytest tests/ -v::TestHomepage`

---

## APP-002 · Signup, Login, Private Dashboard, Logout

### Decisions
| Decision | Choice | Reason |
|----------|--------|--------|
| Auth method | **JWT (Bearer token)** | Ported from At The Helm's Express middleware; matches the security model I already built and understand |
| Password hashing | **bcrypt via passlib** | Standard, same algorithm as At The Helm (bcryptjs) |
| Token storage | **localStorage** | Simple client-side approach; acceptable for this scope |
| Session expiry | **24 hours** | Matches At The Helm |
| Dashboard guard | FastAPI `Depends(get_current_user)` | Server-enforced (401 if no valid token) |
| Logout | Clear localStorage + redirect | Stateless JWT — no server-side revocation needed at this scope |

### Implementation
- Signup API: `POST /auth/signup` → [`app/routers/auth.py`](app/routers/auth.py#L40-L66)
- Login API: `POST /auth/login` → [`app/routers/auth.py`](app/routers/auth.py#L69-L84)
- Dashboard: `GET /dashboard` → [`app/routers/dashboard.py`](app/routers/dashboard.py#L18-L27)
- Auth helpers: [`app/security/auth.py`](app/security/auth.py)

### Check
- Signup creates a `member` user, returns a token — `TestAuth::test_signup_creates_user`
- Login with wrong password returns `401` — `TestAuth::test_login_wrong_password_fails`
- Dashboard without token returns `401` — `TestAuth::test_dashboard_requires_auth`
- Dashboard with valid token returns `200` with username visible — `TestAuth::test_dashboard_accessible_with_token`

---

## APP-003 · Member/Admin Role Enforcement

### Decisions
| Decision | Choice | Reason |
|----------|--------|--------|
| Role model | `anonymous / member / admin` | Directly mirrors At The Helm's 3-tier hierarchy |
| Enforcement | FastAPI `Depends(require_role("admin"))` | Server-side — cannot be bypassed from the browser |
| Role management | **Trusted local CLI** (`python -m app.cli`) | Assignment requires CLI-based role management; keeps admin promotion off the public API |
| Default role | `member` on signup | Safe default — users must be explicitly promoted |

### Implementation
- RBAC dependency: [`app/security/rbac.py`](app/security/rbac.py)
- Admin route: `GET /admin` → [`app/routers/dashboard.py`](app/routers/dashboard.py#L31-L41)
- CLI: [`app/cli.py`](app/cli.py)

### Check
- Anonymous → `/admin` returns `401` — `TestRBAC::test_admin_panel_blocked_for_anonymous`
- Member → `/admin` returns `403` — `TestRBAC::test_admin_panel_blocked_for_member`
- Admin → `/admin` returns `200` with user table — `TestRBAC::test_admin_panel_accessible_for_admin`

```bash
# Promote a user via CLI (run locally)
python -m app.cli list-users
python -m app.cli promote <username> admin
```

---

## GitHub CI
Both jobs (`lint` and `test`) defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) must pass on `main` before submission.
