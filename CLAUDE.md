# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tipset is a learning project — a FastAPI backend with SQLite persistence, built to understand web server fundamentals (routing, validation, ORM, HTTP). There is currently no frontend.

## Commands

All commands run from the `backend/` directory. The project uses `uv` for dependency management.

```bash
# Install dependencies
cd backend && uv sync

# Run the development server (with auto-reload)
cd backend && uv run fastapi dev app/main.py

# Run the server in production mode
cd backend && uv run uvicorn app.main:app
```

The API docs are available at `http://localhost:8000/docs` when the server is running.

## Architecture

Everything lives in `backend/app/main.py` — a single-file FastAPI app. The layers are:

- **Uvicorn** — the ASGI server that listens on a port and receives HTTP requests
- **FastAPI** — defines routes and maps URLs to Python functions
- **Pydantic models** — `NoteCreate` (input validation) and `NoteOut` (response shape)
- **SQLAlchemy ORM** — `Note` class maps to the `notes` SQLite table; `get_db()` is a FastAPI dependency that yields a session per request
- **SQLite** — stored in `backend/app/core/notes.db`

Current endpoints: `GET /`, `GET /health`, `POST /notes`, `GET /notes`, `GET /notes/{note_id}`.

## Dependencies

Managed with `uv` (`pyproject.toml` + `uv.lock`). Python 3.11+ required (pinned in `.python-version`). Key packages: `fastapi[standard]`, `sqlalchemy`.


## Working agreement (teaching mode)
- I am a student learning software end-to-end. Optimize for my understanding, not speed.
- Explain the *why* behind every non-trivial choice as you go (trade-offs, alternatives rejected).
- For load-bearing logic (scoring engine, deadline locking, auth): do NOT write it for me.
  Scaffold and leave the key function for me to implement, then review what I wrote.
- Keep changes in small batches I can review in ~5 minutes.
- I must be able to explain every line that ships. Quiz me occasionally.
