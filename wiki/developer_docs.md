# Developer Documentation

## Overview
File Sorter Enterprise is composed of three main logical components:

1. **Orchestrator (`setup_and_run.py`)**: 
   The main initialization GUI build with `customtkinter`. It sets up standard `.env` values if they don't exist and spawns concurrent system processes.
   
2. **Backend (`src/backend`)**:
   A robust, async-first Python server running on `FastAPI`. 
   - **Database**: Uses `SQLModel` with options for SQLite (Local) or PostgreSQL (Dockerized).
   - **Security**: Handles JWT-based encryption, hashing algorithms with `bcrypt` / `passlib`.

3. **Agent (`src/agent`)**:
   The desktop client built via `customtkinter` with `tkinterdnd2` for drag-and-drop support. It utilizes a `watchdog` to continuously monitor folders and sort items through background tasks via `httpx`/`requests` to the Backend.

## How to Build Docs
Run `python scripts/generate_docs.py` to compile the auto-generated HTML codebase documentation. You will find it inside the `/docs` directory.
