
Yes. Your current README has good technical content, but it reads more like documentation than a strong GitHub project README. For a portfolio project, I’d make the top much more visual and add an architecture diagram, then keep the detailed technical sections underneath.

Here’s a cleaner version you can use:

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


Today 5:59 PM
2963e3fe-fcb0-4c3b-a46b-6807feb04ea3.png
not good  u see the new background that is different than black colour should only be for the dagrams not for the text do it again

Stopped creating image

donot generate image I said fix the read me file

Fixed — the README prose is normal Markdown, and the darker/different background is only used by the architecture/flow diagrams and actual code blocks.

Download the corrected README.md 


README_gitchecker.md
Document

You’re out of data analysis for now. Start a free Plus trial for more, or try again tomorrow after 6:00 PM.
Try Plus free

Library
/
README_gitchecker.md


GitChecker 🔍
AI-Powered Automated Code Bug Detection & Fix Verification
GitChecker analyzes a GitHub repository, finds bugs related to a task, lets the user select an issue, generates a fix, and verifies that fix by running the repository inside an isolated Docker sandbox.

Live Demo: https://git-checker.vercel.app

Overview
GitChecker is built around a simple idea: an AI-generated fix should be tested, not blindly trusted.

The workflow is:

Repository → Bug Detection → User Selection → Code Fix → Docker Verification → Result

The system separates bug discovery from code generation and uses Docker to execute the proposed change in an isolated environment.

Architecture
                         ┌─────────────────────┐
                         │      GitHub Repo     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │       Planner Agent       │
                    │                           │
                    │ Explore repository        │
                    │ Find task-related issues  │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      Issue Selection      │
                    │         Frontend          │
                    └─────────────┬─────────────┘
                                  │
                           User selects
                              one issue
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │        Coder Agent        │
                    │                           │
                    │ Re-read relevant file     │
                    │ Generate corrected code   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      Fix Application      │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │       Docker Sandbox      │
                    │                           │
                    │ Install dependencies      │
                    │ Run tests / entry point   │
                    └─────────────┬─────────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                    ┌─────────┐       ┌─────────┐
                    │ SUCCESS │       │ FAILURE │
                    └────┬────┘       └────┬────┘
                         │                 │
                         ▼                 ▼
                     Verified         Fix Rejected
                         │
                         ▼
                    ┌─────────────┐
                    │   History   │
                    │ PostgreSQL  │
                    └─────────────┘
Key Features
🔎 AI Bug Detection
A Planner Agent explores the repository and identifies issues related to the user's task.

Instead of automatically fixing the first issue found, GitChecker presents the detected issues and lets the user choose which one to address.

🧑‍💻 User-Controlled Fixing
After selecting an issue, the Coder Agent:

Re-reads the relevant source file

Analyzes the selected issue

Generates the corrected file

Returns the proposed change

The coder is intentionally scoped to the files identified by the planner.

🐳 Real Code Verification
GitChecker does not treat an LLM response as proof that a fix works.

The proposed fix is applied to a temporary repository copy and executed inside Docker.

The verification process:

Clones the repository

Creates a working copy

Applies the generated fix

Detects the project language and configuration

Installs dependencies

Runs the project's test suite

Reports whether verification succeeded

🔐 GitHub Authentication
Users authenticate through GitHub OAuth.

Authentication uses HTTP-only JWT cookies, and protected resources additionally verify ownership before allowing modifications or deletion.

📚 Fix History
Verified checks can be saved to the user's history.

Each user's history is isolated so users cannot access or delete another user's saved results.

🧩 Monorepo Support
GitChecker supports projects where the affected code is located inside nested directories such as frontend/ or backend/.

The verification system searches upward from the affected file to locate the nearest project manifest, allowing it to detect the correct environment for nested projects.

AI Pipeline
GitChecker separates repository exploration from structured output and code generation.

                         Repository
                              │
                              ▼
                    ┌──────────────────┐
                    │   Planner Agent  │
                    │                  │
                    │ Explore + reason │
                    │ Find issues      │
                    └────────┬─────────┘
                             │
                             ▼
                       Issue List
                             │
                             ▼
                    User selects issue
                             │
                             ▼
                    ┌──────────────────┐
                    │    Coder Agent   │
                    │                  │
                    │ Read target file │
                    │ Generate fix     │
                    └────────┬─────────┘
                             │
                             ▼
                        Proposed Fix
                             │
                             ▼
                    ┌──────────────────┐
                    │  Docker Sandbox  │
                    │                  │
                    │ Apply + execute  │
                    └────────┬─────────┘
                             │
                             ▼
                       Verification
Why two agents?
The Planner and Coder have different responsibilities.

Planner: understand the repository and identify relevant issues.

Coder: implement one selected fix.

The Coder also re-reads the source file instead of blindly trusting the Planner's description. This keeps each stage focused and limits the amount of repository context given to the coding stage.

Docker Verification
The original repository is never modified.

A temporary copy is created before the fix is applied.

                         Host
                          │
                          ▼
                  Temporary Repo Copy
                          │
                          ▼
                ┌─────────────────────┐
                │    Docker Sandbox   │
                │                     │
                │  Apply generated fix│
                │  Install packages   │
                │  Run tests          │
                └──────────┬──────────┘
                           │
                     ┌─────┴─────┐
                     ▼           ▼
                   PASS         FAIL
                     │           │
                     ▼           ▼
                 Verified     Rejected
Currently supported verification environments:

Python

JavaScript

TypeScript

GitChecker automatically detects the project language, manifest, dependency configuration, test command, and entry point when required.

Authentication Flow
GitHub OAuth provides the user's identity, while the backend manages the application session.

User
 │
 ▼
GitHub OAuth
 │
 ▼
OAuth Callback
 │
 ▼
Backend verifies identity
 │
 ▼
JWT created
 │
 ▼
HTTP-only Cookie
 │
 ▼
Protected API Requests
 │
 ▼
JWT + Resource Ownership Check
Authentication answers who the user is.

Authorization checks whether that user owns the requested resource.

Tech Stack
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

API
Method	Endpoint	Description
GET	/auth/login	Start GitHub OAuth
GET	/auth/callback	Handle OAuth callback
GET	/auth/me	Get current user
POST	/auth/logout	End session
POST	/check/start	Analyze repository and find issues
POST	/check/fix	Generate and verify selected fix
POST	/check/save	Save an unverified fix
GET	/check/history	Retrieve user's history
DELETE	/check/history/{id}	Delete a history entry
Running Locally
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
Create backend/.env with your database, authentication, Anthropic, and GitHub OAuth credentials.

Frontend
cd frontend
npm install
npm run dev
Create frontend/.env:

VITE_API_URL=http://localhost:8000
The frontend will run at http://localhost:5173.

Testing
The backend test suite focuses on deterministic components that can be tested reliably without depending on live LLM responses.

Tests cover:

Language detection

Manifest and project detection

Test command detection

Nested repository structures

Fix application

JWT creation and validation

Token expiration

Invalid and tampered tokens

Protected route behavior

Run the backend tests with:

cd backend
uv run pytest
LLM and Docker-dependent functionality is primarily validated through end-to-end testing with real repositories.

Limitations
Performance Bugs
Static code analysis cannot replace runtime profiling, so GitChecker is not currently reliable for diagnosing performance regressions.

One Issue Per Fix
Each fix starts from a fresh repository clone. Multiple fixes cannot currently be chained together in a single session.

Test-Based Verification
Verification currently checks whether the project's test suite or entry point exits successfully. It does not yet generate a dedicated regression test proving that the specific issue was fixed.

Roadmap
Before/after test comparison

Automatic regression-test generation

Support for additional programming languages

Session-based multi-fix workflows

Frontend test coverage

Improved runtime and performance analysis

License
This project is for portfolio and demonstration purposes.

All rights reserved.

