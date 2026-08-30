# GitChecker 🔍

Agentic AI tool that clones a public GitHub repo, finds real bugs related to a task you describe, and lets you pick one to fix — then verifies the fix by actually running your test suite inside an isolated Docker container.

**Live Demo:** [https://git-checker.vercel.app](https://git-checker.vercel.app) **Backend API:** [https://api.47-129-86-136.nip.io](https://api.47-129-86-136.nip.io)

> Note: the backend runs on AWS EC2 t3 small instance.

---

## ✨ Features

- **Multi-issue detection** — a planner agent explores the repo and reports every real issue it finds related to your task, not just one
- **User-selected fixing** — you choose which issue to fix; a coder agent generates a complete corrected version of the file
- **Real verification, not a guess** — the proposed fix is applied to a cloned copy of the repo and run inside a Docker container against the project's actual test suite (or entry point if no tests exist)
- **Automatic language & command detection** — detects Python/JavaScript/TypeScript, install commands, test runners, and entry points, including in nested fullstack repos (`backend/`, `frontend/` subfolders)
- **GitHub OAuth login** — session-based auth via HTTP-only JWT cookies
- **History** — every verified check is saved per-user, viewable and deletable, with ownership enforced on every request
- **Unsupported-language handling** — if a language can't be verified in-sandbox, the fix is shown as a proposal only, with an explicit opt-in to save it anyway

---

## 🛠️ Tech Stack

### Frontend
- React + TypeScript + Vite
- TanStack Query (data fetching & caching)
- React Router
- Tailwind CSS + shadcn/ui + Base UI
- Axios

### Backend
- FastAPI (Python)
- LangChain (tool-calling agents + structured output)
- Anthropic Claude API
- SQLAlchemy (async) + PostgreSQL
- Docker SDK for Python (sandboxed fix verification)
- JWT authentication via HTTP-only cookies

### Infrastructure
- **Database:** Neon (Serverless PostgreSQL)
- **Backend Hosting:** AWS EC2, behind nginx (reverse proxy) with a free Let's Encrypt certificate via Certbot
- **Frontend Hosting:** Vercel
- **CI/CD:** GitHub Actions (runs backend pytest suite + frontend build checks on every push to `main`)

---

## 🧠 How It Works

GitChecker uses a two-agent pipeline instead of a single model call, specifically to avoid a class of bug where an agent's free-form reasoning corrupts strict JSON output:

1. **Explore step** — an agent with file-reading tools investigates the repo in plain language (no formatting constraints, so it can reason freely)
2. **Structure step** — a separate, tool-less call converts that plain-language analysis into a strict, schema-validated response

This runs twice per check:

- **Planner** — explores the repo, returns a list of every issue it finds related to your task
- **Coder** — given one issue you selected, re-reads the relevant file fresh and returns the complete corrected file content

The coder always re-reads files itself rather than trusting the planner's summary, and is only given the file paths the planner already pointed to (it can't browse the repo freely) — keeping its scope intentionally narrow.

---

## 🐳 How Verification Works

1. The repo is cloned to a temporary directory
2. The proposed fix is written into a **copy** of that directory (the original is never touched until verification passes)
3. The language and the correct install/test command are detected — including walking up from the fixed file's own directory to find the nearest manifest (`package.json`, `requirements.txt`, etc.), so fixes inside a `backend/` or `frontend/` subfolder of a monorepo are still verified correctly
4. A fresh Docker container (`python:3.13-slim`, `python:3.14-slim` or `node:22-slim`) installs dependencies and runs the real test suite (or entry point if no tests are found)
5. Only if the container exits successfully is the fix reported as verified and saved to history

If the detected language isn't supported for sandboxing, the fix is still shown, clearly labeled as **unverified**, with an explicit choice to save it anyway.

---

## 🔑 How Authentication Works

- Login goes through GitHub OAuth; on callback, the backend signs a JWT and sets it as an HTTP-only, `SameSite=None; Secure` cookie (required since the frontend and backend are on different domains)
- On app load, the frontend calls `GET /auth/me` — the cookie is sent automatically
- A FastAPI dependency (`get_currentUser_id`) verifies the cookie on every protected route and returns the user's ID
- Every mutating request that touches a specific resource (e.g. deleting a history entry) re-checks that the resource actually belongs to the requesting user — authentication alone doesn't guarantee authorization, so this is checked explicitly rather than assumed
- Logout clears the cookie

---

## 🚀 Running Locally

### Prerequisites
- Python 3.13+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22+
- Docker (running locally — required for fix verification)
- A PostgreSQL database (or a free [Neon](https://neon.tech) instance)
- An [Anthropic API key](https://console.anthropic.com/)
- A [GitHub OAuth App](https://github.com/settings/developers)

### Backend
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

Create a `.env` file in `backend/`:
```
DATABASE_URL=your_postgres_connection_string
JWT_SECRET=your_jwt_secret
ANTHROPIC_API_KEY=your_anthropic_api_key
PLANNER_MODEL=claude-sonnet-5
CODER_MODEL=claude-sonnet-4-6
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Create a `.env` file in `frontend/`:
```
VITE_API_URL=http://localhost:8000
```

The app will be running at `http://localhost:5173`.

---

## 📡 API Overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/auth/login` | Redirects to GitHub OAuth |
| GET | `/auth/callback` | GitHub OAuth callback, sets session cookie |
| GET | `/auth/me` | Get current logged-in user |
| POST | `/auth/logout` | Clear auth cookie |
| POST | `/check/start` | Clone a repo and get a list of issues found for a given task |
| POST | `/check/fix` | Generate and verify a fix for one selected issue |
| POST | `/check/save` | Save an unverified (unsupported-language) fix to history anyway |
| GET | `/check/history` | Get all saved checks for the current user |
| DELETE | `/check/history/{id}` | Delete a saved check (only if owned by the requesting user) |

All `/check/*` routes and `/auth/me`/`/auth/logout` require authentication via the JWT cookie.

---

## 🧪 Testing

Unit tests focus on the deterministic, dependency-free core rather than trying to unit-test LLM or Docker-dependent code directly:

- **Language & command detection** — extension mapping, config-file scanning, and nested-repo manifest lookup (walking up from the fixed file's directory)
- **Fix application** — writing the corrected file into a repo copy, including edge cases like a missing target file
- **Authentication boundary** — token creation/decoding (tampering, expiry, wrong-secret forgery), and route-level rejection of missing/invalid sessions

LLM-calling and Docker-dependent code paths (the agents themselves, sandbox execution) are covered through manual end-to-end testing against real repositories instead — including full-stack repos with nested `backend/`/`frontend` structures, repos with no bugs, unsupported languages, and a real open-source issue from a large codebase (`processing/p5.js`) to test behavior on unfamiliar, non-trivial code.

Run tests:
```bash
cd backend
uv run pytest
```

---

## ⚠️ Known Limitations

- **Not reliable for performance-regression bugs.** Tested against a real, maintainer-confirmed performance issue in a large open-source repo — the tool produced a plausible-sounding but incorrect root cause, since it reasons from static code reading rather than actual runtime profiling.
- **One issue fixed at a time.** Each fix is verified against a fresh clone of the repo; fixes aren't chained or applied cumulatively across multiple issues in one session.
- **Exact test-suite state, not fix-specific pass/fail.** Verification currently checks whether the full test suite exits cleanly after a fix, not whether the specific failing test related to the issue now passes in isolation.

---

## 🗺️ Roadmap

- [ ] Diff-based before/after test comparison, instead of relying on full test-suite exit code
- [ ] Support for additional languages in the sandbox
- [ ] Session-grouped history (see all issues fixed from one repo check together)
- [ ] Frontend test coverage

---

## 📄 License

This project is for portfolio/demonstration purposes. All rights reserved — please do not copy or redistribute as your own work.
