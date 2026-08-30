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

Method

Endpoint

Description

GET

/auth/login

Start GitHub OAuth

GET

/auth/callback

Handle OAuth callback

GET

/auth/me

Get current user

POST

/auth/logout

End session

POST

/check/start

Analyze repository and find issues

POST

/check/fix

Generate and verify selected fix

POST

/check/save

Save an unverified fix

GET

/check/history

Retrieve user's history

DELETE

/check/history/{id}

Delete a history entry

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
