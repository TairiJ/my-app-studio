# LEARNING.md – At The Helm App Studio
## IS373 App Studio · Personal Reflections

---

## APP-001 · Branded Homepage

**Decision I made:** I reused the "At The Helm" brand I'd already built for another project. The name, archetype ("The Commander"), and tagline were already established, so I didn't need to invent them — I just had to translate them into FastAPI + Jinja2 templates.

**What I observed in the browser:** The homepage loads at `http://localhost:8000`. It shows the ⚓ logo text, the brand tagline, three feature cards (Role-Based Access, Secure Auth, FastAPI Speed), and two CTA buttons linking to sign-up and login. The dark cockpit theme matches the original At The Helm React UI visually.

**What surprised me:** FastAPI's Jinja2 integration is very simple — you just pass a `templates` directory and return `TemplateResponse`. In React I was used to component trees; here it's just a single HTML file with `{{ variable }}` slots. Much less abstraction for simple pages like this.

---

## APP-002 · Signup, Login, Private Dashboard, Logout

**Decision I made:** I used JWT Bearer tokens, the same approach I had in At The Helm's Express backend. The logic is nearly identical — `bcrypt` to hash passwords, `jose`/`jwt` to create and verify tokens — the difference is that FastAPI uses Python's `Depends()` injection system instead of Express middleware chaining.

**What I observed in the browser:** 
- Navigating to `/dashboard` without logging in redirects to the login page (the JS guard in the template detects no token in localStorage and redirects).
- After signing up, I land on the dashboard immediately with my username displayed and my role shown as `member` in a green badge.
- Clicking "Log out" clears the token from localStorage and sends me back to the homepage.

**What I noticed comparing the two stacks:** In Express, auth middleware runs for every request and you check `req.user`. In FastAPI, `Depends(get_current_user)` does the same thing but it's declared per-route, which makes it more explicit — you can see from the function signature alone whether a route requires auth.

---

## APP-003 · Role Enforcement + CLI

**Decision I made:** I enforced roles entirely on the server using `Depends(require_role("admin"))`. I deliberately chose NOT to trust the client for access control — the JWT carries the role, but the server always re-validates it against the database value.

**What I observed in the browser:**
- Logging in as a `member` and manually navigating to `/admin` returns a FastAPI `403 Forbidden` JSON response — the page never loads.
- After running `python -m app.cli promote myuser admin` in the terminal and logging back in, `/admin` loads with the full user table.
- The admin panel shows each user's role badge (red for admin, green for member) and the CLI instructions right on the page.

**Honest reflection:** The hardest part was understanding how FastAPI's dependency override works in tests — you replace `get_session` with a test-database version so the app never touches the real `helm.db`. Once I understood that pattern, writing the RBAC tests became straightforward. The same kind of test isolation was harder to set up in the Express project because we had to mock the entire database module.

---

## Overall Takeaway

Reusing the At The Helm brand accelerated APP-001 (zero brand decisions needed). The auth and RBAC patterns translated directly from Express/TypeScript to FastAPI/Python — the concepts are identical, only the syntax changes. The biggest learning was FastAPI's dependency injection, which is cleaner than Express middleware for per-route access control because the security requirements are visible in the function signature rather than in a separate middleware stack.
