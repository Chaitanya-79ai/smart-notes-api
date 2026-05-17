# Notes App Backend API

A FastAPI backend for a multi-user notes application. It supports user registration, JWT-based authentication, note CRUD operations, note sharing, keyword search, and a custom Smart Action Item Extraction feature.

## Live Demo

Base URL:

```text
https://smart-notes-api-0z6x.onrender.com
```

## Project Overview

This project was built as a backend API for a notes app.

Users can register, log in, create notes, view notes, update notes, delete notes, and share notes with another registered user.

## Custom Feature: Smart Action Item Extraction

I added a custom feature called **Smart Action Item Extraction**.

Endpoint:

```text
GET /notes/{note_id}/actions
```

This feature extracts possible tasks from a note using lightweight NLP-style rules.

Example note content:

```text
I need to review the authentication flow once more. Tomorrow I need to finish the deployment work and push the final code to GitHub. I must update the README with setup instructions.
```

Example response:

```json
{
  "note_id": 3,
  "action_items": [
    "review the authentication flow once more",
    "finish the deployment work and push the final code to GitHub",
    "update the README with setup instructions"
  ]
}
```

I chose this feature because notes often contain hidden todos. Turning long note content into clear action items makes the app more useful and productivity-focused.

## Features

- User registration
- User login with JWT authentication
- Create notes
- Get all notes for authenticated user
- Get a specific note by ID
- Update notes
- Delete notes
- Share notes with another registered user
- Search notes by keyword
- Smart Action Item Extraction
- OpenAPI JSON at `/openapi.json`
- About endpoint at `/about`

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- JWT authentication
- bcrypt password hashing
- Pydantic validation


## Architecture

```text
Client / Swagger UI / API Tester
        |
        v
FastAPI Application
        |
        |-- main.py       -> API routes and request handling
        |-- auth.py       -> JWT authentication and password hashing
        |-- schemas.py    -> Request and response validation
        |-- models.py     -> SQLAlchemy database models
        |-- database.py   -> Database engine and session management
        |-- config.py     -> Environment variable loading
        |
        v
SQLite Database
        |
        |-- users
        |-- notes
        |-- shared_notes
```

The application follows a simple layered backend structure:

- `main.py`: Defines FastAPI routes and request handling logic.
- `models.py`: Defines SQLAlchemy database models for users, notes, and shared notes.
- `schemas.py`: Defines Pydantic request and response schemas for validation.
- `auth.py`: Handles password hashing, JWT token creation, and authentication.
- `database.py`: Manages database engine, sessions, and connection setup.
- `config.py`: Loads environment variables such as database URL and JWT settings.

The API uses JWT-based authentication. After login, the client sends the access token in the `Authorization` header for protected endpoints.

SQLite is used as the database for simplicity. SQLAlchemy is used as the ORM layer to interact with the database.

Note sharing is implemented using a separate `shared_notes` table. This allows a note owner to share a note with another registered user while keeping update and delete permissions restricted to the owner.

The Smart Action Item Extraction feature is implemented as a lightweight text-processing layer that reads note content, detects task-like sentences using predefined action keywords, and returns extracted action items.

## Local Setup

Create and activate virtual environment:

```bash
uv venv --python 3.12 venv
source venv/bin/activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Open OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=change-this-to-a-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./notes.db
```

## Access Control

- Users can read, update, delete, and share only their own notes.
- Shared users can read notes shared with them.
- Shared users can use the action extraction endpoint on shared notes.
- Shared users cannot update or delete notes they do not own.

## API Documentation

Detailed endpoint documentation will be maintained separately in `API_DOCS.md`.
