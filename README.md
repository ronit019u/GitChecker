# GitChecker 🔍

### AI-Powered Automated Code Bug Detection & Fix Verification

GitChecker is an AI-powered developer tool that analyzes a GitHub repository, identifies bugs related to a developer's task, generates a fix for a selected issue, and verifies the fix by running the repository's actual tests inside an isolated Docker sandbox.

**Live Demo:** https://git-checker.vercel.app

---

## 📌 Overview

Instead of simply asking an LLM to "fix this code", GitChecker creates a controlled pipeline:

**GitHub Repository → AI Analysis → Issue Selection → AI Fix → Docker Verification → Verified Result**

The system separates **bug discovery** from **code generation** and uses an isolated execution environment to determine whether the generated fix actually works.

---

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      GitHub Repo    │
                         └──────────┬──────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────┐
│                       GitChecker                         │
│                                                          │
│  ┌───────────────┐       ┌──────────────────────────┐   │
│  │    Planner    │──────▶│   Issue Selection        │   │
│  │     Agent     │       │      (Frontend)          │   │
│  └───────────────┘       └────────────┬─────────────┘   │
│                                       │                 │
│                                       ▼                 │
│                              ┌────────────────┐         │
│                              │  Coder Agent   │         │
│                              └───────┬────────┘         │
│                                      │                  │
│                                      ▼                  │
│                              ┌────────────────┐         │
│                              │ Fix Application │         │
│                              └───────┬────────┘         │
│                                      │                  │
│                                      ▼                  │
│                              ┌────────────────┐         │
│                              │ Docker Sandbox │         │
│                              │                │         │
│                              │ Install deps   │         │
│                              │ Run tests      │         │
│                              └───────┬────────┘         │
│                                      │                  │
│                         ┌────────────┴────────────┐     │
│                         ▼                         ▼     │
│                    Verification                Failure  │
│                    Successful                  / Retry  │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
                 ┌─────────────────┐
                 │  History / DB   │
                 └─────────────────┘
✨ Key Features
🔎 AI Bug Detection
The Planner Agent explores the repository and identifies issues relevant to the developer's task.

Instead of automatically choosing an issue, GitChecker returns multiple findings and lets the user decide which one should be fixed.

🧑‍💻 User-Controlled Fixing
The user selects a specific issue from the planner's findings.

The Coder Agent then:

Re-reads the relevant source file

Analyzes the selected issue

Generates the corrected file

Returns the proposed fix

🐳 Real Code Verification
Generated code is not considered correct simply because the LLM says it is.

GitChecker:

Clones the repository

Creates a working copy

Applies the generated fix

Detects the project's language and tooling

Installs dependencies

Runs the project's tests inside Docker

Reports whether the fix successfully passes verification

🔐 Secure Authentication
GitHub OAuth is used for authentication.

Sessions are maintained using HTTP-only JWT cookies, while resource ownership is checked on protected operations.

📚 Fix History
Verified fixes can be stored and viewed later.

Each user's history is isolated so users cannot access or delete another user's saved results.

🧩 Monorepo Support
GitChecker can detect project configuration inside nested directories such as:

repository/
├── frontend/
│   ├── package.json
│   └── ...
│
└── backend/
    ├── pyproject.toml
    └── ...
The verification system searches upward from the affected file to locate the nearest project manifest.

🧠 AI Pipeline
GitChecker uses separate AI stages instead of relying on a single LLM call.

Repository
     │
     ▼
┌──────────────┐
│    Planner   │
│              │
│ Explore repo │
│ Find issues  │
└──────┬───────┘
       │
       ▼
   Issue List
       │
       ▼
 User selects issue
       │
       ▼
┌──────────────┐
│     Coder    │
│              │
│ Read file    │
│ Generate fix │
└──────┬───────┘
       │
       ▼
 Proposed Fix
       │
       ▼
┌──────────────┐
│    Docker    │
│   Sandbox    │
│              │
│ Run tests    │
└──────┬───────┘
       │
       ▼
   Verification
Why separate Planner and Coder agents?
The Planner is responsible for finding and explaining problems, while the Coder is responsible for implementing one selected fix.

This separation keeps each agent's responsibility narrow and allows the user to remain in control of which issue gets modified.

The Coder also re-reads the relevant source file instead of blindly relying on the Planner's description.

🐳 Docker Verification
The verification environment is isolated from the host system.

                    Host System
                         │
                         ▼
                ┌─────────────────┐
                │ Temporary Repo   │
                │     Copy         │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Docker Sandbox  │
                │                 │
                │ Install deps    │
                │ Apply fix       │
                │ Run tests       │
                └────────┬────────┘
                         │
                  ┌──────┴──────┐
                  ▼             ▼
                PASS           FAIL
                  │             │
                  ▼             ▼
              Verified       Rejected
The original repository is never modified.

Currently supported verification environments include:

Python

JavaScript

TypeScript

The system automatically detects:

Programming language

Package manager / dependency configuration

Project manifest

Test framework

Test command

Application entry point when no tests are available

🛠️ Tech Stack
Frontend
React

TypeScript

Vite

TanStack Query

React Router

Tailwind CSS

shadcn/ui

Axios

Backend
Python

FastAPI

SQLAlchemy

PostgreSQL

LangChain

Anthropic Claude

GitPython

Docker SDK

JWT Authentication

Infrastructure
Database: Neon PostgreSQL

Backend: AWS EC2

Reverse Proxy: nginx

TLS: Let's Encrypt / Certbot

Frontend: Vercel

CI/CD: GitHub Actions

Sandbox: Docker

🔐 Authentication Flow
User
 │
 ▼
GitHub OAuth
 │
 ▼
GitHub Callback
 │
 ▼
Backend
 │
 ├── Verify GitHub identity
 │
 └── Create JWT
        │
        ▼
 HTTP-only Cookie
        │
        ▼
 Protected API Routes
Every protected request validates the JWT.

For operations involving stored resources, GitChecker additionally verifies that the resource belongs to the authenticated user.

This provides both:

Authentication → Who are you?

Authorization → Are you allowed to access this resource?

📡 API
Method	Endpoint	Purpose
GET	/auth/login	Start GitHub OAuth
GET	/auth/callback	Handle OAuth callback
GET	/auth/me	Get current user
POST	/auth/logout	End session
POST	/check/start	Analyze repository and find issues
POST	/check/fix	Generate and verify selected fix
POST	/check/save	Save an unverified fix
GET	/check/history	Retrieve user's history
DELETE	/check/history/{id}	Delete a history entry
🚀 Running Locally
Requirements
Python 3.13+

uv

Node.js 18+

Docker

PostgreSQL

Anthropic API key

GitHub OAuth application

Backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
Create backend/.env:

DATABASE_URL=your_postgres_connection_string
JWT_SECRET=your_jwt_secret
ANTHROPIC_API_KEY=your_anthropic_api_key

PLANNER_MODEL=claude-sonnet-4-6
CODER_MODEL=claude-sonnet-4-6

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
Frontend
cd frontend
npm install
npm run dev
Create frontend/.env:

VITE_API_URL=http://localhost:8000
The application will be available at:

http://localhost:5173
🧪 Testing
The backend test suite focuses primarily on deterministic components.

Tests cover:

Language detection

Project/manifest detection

Test command detection

Nested repository structures

Fix application

Authentication token creation

Token validation

Token expiration

Invalid/tampered tokens

Protected route behavior

Run:

cd backend
uv run pytest
LLM and Docker-dependent functionality is primarily tested through end-to-end testing with real repositories.

⚠️ Limitations
Performance Bugs
GitChecker is not designed to reliably diagnose performance regressions because static code analysis cannot replace runtime profiling.

One Issue Per Fix
Each fix starts from a fresh repository clone. Multiple issues cannot currently be fixed cumulatively in the same session.

Test-Based Verification
Verification currently determines success based on the project's test/entry-point execution rather than proving that the specific issue was fixed by a dedicated regression test.

🗺️ Roadmap
 Before/after test comparison

 Automatic regression-test generation

 Support for more programming languages

 Session-based multi-fix workflows

 Frontend test coverage

 Improved runtime/performance analysis

📄 License
This project is for portfolio and demonstration purposes.

All rights reserved.


### One thing I would strongly recommend

For your GitHub repo, put an actual **architecture image** immediately after the Overview rather than relying only on the ASCII diagram.

Your README would then have this structure:

```text
GitChecker
│
├── Short description
├── Live Demo
│
├── Overview
│
├── Architecture Diagram ⭐
│
├── Key Features
│
├── AI Pipeline
│
├── Docker Verification
│
├── Tech Stack
│
├── Authentication
│
├── API
│
├── Local Development
│
├── Testing
│
├── Limitations
│
└── Roadmap
That makes it look much more like a real engineering project rather than a collection of implementation notes.


Yesterday 10:13 AM
can u give me in readme file

Absolutely. I can give you the complete content as a README.md file.


generate

Done.

Download the README.md 


README.md
Document


Library
/
README.md


GitChecker 🔍
AI-Powered Automated Code Bug Detection & Fix Verification
GitChecker is an AI-powered developer tool that analyzes a GitHub repository, identifies bugs related to a developer's task, generates a fix for a selected issue, and verifies the fix by running the repository's actual tests inside an isolated Docker sandbox.

Live Demo: https://git-checker.vercel.app

📌 Overview
Instead of simply asking an LLM to "fix this code", GitChecker creates a controlled pipeline:

GitHub Repository → AI Analysis → Issue Selection → AI Fix → Docker Verification → Verified Result

The system separates bug discovery from code generation and uses an isolated execution environment to determine whether the generated fix actually works.

🏗️ Architecture
                         ┌─────────────────────┐
                         │      GitHub Repo    │
                         └──────────┬──────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────┐
│                       GitChecker                         │
│                                                          │
│  ┌───────────────┐       ┌──────────────────────────┐   │
│  │    Planner    │──────▶│   Issue Selection        │   │
│  │     Agent     │       │      (Frontend)          │   │
│  └───────────────┘       └────────────┬─────────────┘   │
│                                       │                 │
│                                       ▼                 │
│                              ┌────────────────┐         │
│                              │  Coder Agent   │         │
│                              └───────┬────────┘         │
│                                      │                  │
│                                      ▼                  │
│                              ┌────────────────┐         │
│                              │ Fix Application│         │
│                              └───────┬────────┘         │
│                                      │                  │
│                                      ▼                  │
│                              ┌────────────────┐         │
│                              │ Docker Sandbox │         │
│                              │                │         │
│                              │ Install deps   │         │
│                              │ Run tests      │         │
│                              └───────┬────────┘         │
│                                      │                  │
│                         ┌────────────┴────────────┐     │
│                         ▼                         ▼     │
│                    Verification                Failure  │
│                    Successful                  / Retry  │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
                 ┌─────────────────┐
                 │  History / DB   │
                 └─────────────────┘
✨ Key Features
🔎 AI Bug Detection
The Planner Agent explores the repository and identifies issues relevant to the developer's task.

Instead of automatically choosing an issue, GitChecker returns multiple findings and lets the user decide which one should be fixed.

🧑‍💻 User-Controlled Fixing
The user selects a specific issue from the planner's findings.

The Coder Agent then:

Re-reads the relevant source file

Analyzes the selected issue

Generates the corrected file

Returns the proposed fix

🐳 Real Code Verification
Generated code is not considered correct simply because the LLM says it is.

GitChecker:

Clones the repository

Creates a working copy

Applies the generated fix

Detects the project's language and tooling

Installs dependencies

Runs the project's tests inside Docker

Reports whether the fix successfully passes verification

🔐 Secure Authentication
GitHub OAuth is used for authentication.

Sessions are maintained using HTTP-only JWT cookies, while resource ownership is checked on protected operations.

📚 Fix History
Verified fixes can be stored and viewed later.

Each user's history is isolated so users cannot access or delete another user's saved results.

🧩 Monorepo Support
GitChecker can detect project configuration inside nested directories such as:

repository/
├── frontend/
│   ├── package.json
│   └── ...
│
└── backend/
    ├── pyproject.toml
    └── ...
The verification system searches upward from the affected file to locate the nearest project manifest.

🧠 AI Pipeline
GitChecker uses separate AI stages instead of relying on a single LLM call.

Repository
     │
     ▼
┌──────────────┐
│    Planner   │
│              │
│ Explore repo │
│ Find issues  │
└──────┬───────┘
       │
       ▼
   Issue List
       │
       ▼
 User selects issue
       │
       ▼
┌──────────────┐
│     Coder    │
│              │
│ Read file    │
│ Generate fix │
└──────┬───────┘
       │
       ▼
 Proposed Fix
       │
       ▼
┌──────────────┐
│    Docker    │
│   Sandbox    │
│              │
│ Run tests    │
└──────┬───────┘
       │
       ▼
   Verification
Why separate Planner and Coder agents?
The Planner is responsible for finding and explaining problems, while the Coder is responsible for implementing one selected fix.

This separation keeps each agent's responsibility narrow and allows the user to remain in control of which issue gets modified.

The Coder also re-reads the relevant source file instead of blindly relying on the Planner's description.

🐳 Docker Verification
The verification environment is isolated from the host system.

                    Host System
                         │
                         ▼
                ┌─────────────────┐
                │ Temporary Repo  │
                │      Copy       │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Docker Sandbox  │
                │                 │
                │ Install deps    │
                │ Apply fix       │
                │ Run tests       │
                └────────┬────────┘
                         │
                  ┌──────┴──────┐
                  ▼             ▼
                PASS           FAIL
                  │             │
                  ▼             ▼
              Verified       Rejected
The original repository is never modified.

Currently supported verification environments include:

Python

JavaScript

TypeScript

The system automatically detects:

Programming language

Package manager / dependency configuration

Project manifest

Test framework

Test command

Application entry point when no tests are available

🛠️ Tech Stack
Frontend
React

TypeScript

Vite

TanStack Query

React Router

Tailwind CSS

shadcn/ui

Axios

Backend
Python

FastAPI

SQLAlchemy

PostgreSQL

LangChain

Anthropic Claude

GitPython

Docker SDK

JWT Authentication

Infrastructure
Database: Neon PostgreSQL

Backend: AWS EC2

Reverse Proxy: nginx

TLS: Let's Encrypt / Certbot

Frontend: Vercel

CI/CD: GitHub Actions

Sandbox: Docker

🔐 Authentication Flow
User
 │
 ▼
GitHub OAuth
 │
 ▼
GitHub Callback
 │
 ▼
Backend
 │
 ├── Verify GitHub identity
 │
 └── Create JWT
        │
        ▼
 HTTP-only Cookie
        │
        ▼
 Protected API Routes
Every protected request validates the JWT.

For operations involving stored resources, GitChecker additionally verifies that the resource belongs to the authenticated user.

This provides both:

Authentication → Who are you?

Authorization → Are you allowed to access this resource?

📡 API
Method	Endpoint	Purpose
GET	/auth/login	Start GitHub OAuth
GET	/auth/callback	Handle OAuth callback
GET	/auth/me	Get current user
POST	/auth/logout	End session
POST	/check/start	Analyze repository and find issues
POST	/check/fix	Generate and verify selected fix
POST	/check/save	Save an unverified fix
GET	/check/history	Retrieve user's history
DELETE	/check/history/{id}	Delete a history entry
🚀 Running Locally
Requirements
Python 3.13+

uv

Node.js 18+

Docker

PostgreSQL

Anthropic API key

GitHub OAuth application

Backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
Create backend/.env:

DATABASE_URL=your_postgres_connection_string
JWT_SECRET=your_jwt_secret
ANTHROPIC_API_KEY=your_anthropic_api_key

PLANNER_MODEL=claude-sonnet-4-6
CODER_MODEL=claude-sonnet-4-6

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
Frontend
cd frontend
npm install
npm run dev
Create frontend/.env:

VITE_API_URL=http://localhost:8000
The application will be available at:

http://localhost:5173
🧪 Testing
The backend test suite focuses primarily on deterministic components.

Tests cover:

Language detection

Project/manifest detection

Test command detection

Nested repository structures

Fix application

Authentication token creation

Token validation

Token expiration

Invalid/tampered tokens

Protected route behavior

Run:

cd backend
uv run pytest
LLM and Docker-dependent functionality is primarily tested through end-to-end testing with real repositories.

⚠️ Limitations
Performance Bugs
GitChecker is not designed to reliably diagnose performance regressions because static code analysis cannot replace runtime profiling.

One Issue Per Fix
Each fix starts from a fresh repository clone. Multiple issues cannot currently be fixed cumulatively in the same session.

Test-Based Verification
Verification currently determines success based on the project's test/entry-point execution rather than proving that the specific issue was fixed by a dedicated regression test.

🗺️ Roadmap
Before/after test comparison

Automatic regression-test generation

Support for more programming languages

Session-based multi-fix workflows

Frontend test coverage

Improved runtime/performance analysis

📄 License
This project is for portfolio and demonstration purposes.

All rights reserved.

