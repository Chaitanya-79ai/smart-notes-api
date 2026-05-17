

# API Documentation

Base URL for local development:

```text
http://127.0.0.1:8000
```

For deployed usage, replace the local base URL with the deployed application URL.

## Authentication

Protected endpoints require a JWT access token in the request header:

```http
Authorization: Bearer <access_token>
```

The access token is returned by the `/login` endpoint.

---

## 1. Health Check

```http
GET /
```

### Response

```json
{
  "message": "Notes API is running"
}
```

---

## 2. Register New User

```http
POST /register
```

### Request Body

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Success Response

Status code: `201 Created`

```json
{
  "message": "User registered successfully"
}
```

### Error Cases

- Duplicate email: `400 Bad Request`
- Invalid email format: `422 Unprocessable Entity`
- Password shorter than 6 characters: `422 Unprocessable Entity`

---

## 3. Login

```http
POST /login
```

### Request Body

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Success Response

Status code: `200 OK`

```json
{
  "access_token": "jwt_token_here"
}
```

### Error Response

Status code: `401 Unauthorized`

```json
{
  "detail": {
    "message": "Invalid email or password"
  }
}
```

---

## 4. Create Note

```http
POST /notes
Authorization: Bearer <access_token>
```

### Request Body

```json
{
  "title": "Interview Prep",
  "content": "I need to revise FastAPI and deploy the app."
}
```

### Success Response

Status code: `201 Created`

```json
{
  "id": 1,
  "title": "Interview Prep",
  "content": "I need to revise FastAPI and deploy the app.",
  "created_at": "2026-05-17T10:30:00",
  "updated_at": "2026-05-17T10:30:00"
}
```

---

## 5. Get All Notes

```http
GET /notes
Authorization: Bearer <access_token>
```

### Success Response

Status code: `200 OK`

```json
[
  {
    "id": 1,
    "title": "Interview Prep",
    "content": "I need to revise FastAPI and deploy the app.",
    "created_at": "2026-05-17T10:30:00",
    "updated_at": "2026-05-17T10:30:00"
  }
]
```

Note: This endpoint returns notes created by the authenticated user.

---

## 6. Get Note by ID

```http
GET /notes/{note_id}
Authorization: Bearer <access_token>
```

### Success Response

Status code: `200 OK`

```json
{
  "id": 1,
  "title": "Interview Prep",
  "content": "I need to revise FastAPI and deploy the app.",
  "created_at": "2026-05-17T10:30:00",
  "updated_at": "2026-05-17T10:30:00"
}
```

### Access Rule

The note can be accessed if:

- The authenticated user owns the note.
- The note has been shared with the authenticated user.

### Error Response

Status code: `404 Not Found`

```json
{
  "detail": "Note not found"
}
```

---

## 7. Update Note

```http
PUT /notes/{note_id}
Authorization: Bearer <access_token>
```

### Request Body

```json
{
  "title": "Updated Interview Prep",
  "content": "Revise FastAPI auth, SQLAlchemy models, CRUD APIs and deployment."
}
```

### Success Response

Status code: `200 OK`

```json
{
  "id": 1,
  "title": "Updated Interview Prep",
  "content": "Revise FastAPI auth, SQLAlchemy models, CRUD APIs and deployment.",
  "created_at": "2026-05-17T10:30:00",
  "updated_at": "2026-05-17T10:45:00"
}
```

### Access Rule

Only the note owner can update the note.

---

## 8. Delete Note

```http
DELETE /notes/{note_id}
Authorization: Bearer <access_token>
```

### Success Response

Status code: `204 No Content`

### Access Rule

Only the note owner can delete the note.

---

## 9. Share Note

```http
POST /notes/{note_id}/share
Authorization: Bearer <access_token>
```

### Request Body

```json
{
  "share_with_email": "shared-user@example.com"
}
```

### Success Response

Status code: `200 OK`

```json
{
  "message": "Note shared successfully"
}
```

### Access Rule

Only the note owner can share the note.

### Error Cases

- Note not found: `404 Not Found`
- User to share with not found: `404 Not Found`
- Sharing with yourself: `400 Bad Request`
- Note already shared with this user: `400 Bad Request`

---

## 10. Search Notes

```http
GET /search?q=keyword
Authorization: Bearer <access_token>
```

### Example

```http
GET /search?q=FastAPI
```

### Success Response

Status code: `200 OK`

```json
[
  {
    "id": 2,
    "title": "FastAPI Deployment",
    "content": "Render deployment and OpenAPI testing",
    "created_at": "2026-05-17T11:00:00",
    "updated_at": "2026-05-17T11:00:00"
  }
]
```

Note: Search checks the authenticated user's own notes by title and content.

---

## 11. Smart Action Item Extraction

```http
GET /notes/{note_id}/actions
Authorization: Bearer <access_token>
```

This endpoint extracts possible tasks from a note using lightweight NLP-style rules.

### Example Note Content

```text
I need to review the authentication flow once more and check whether invalid tokens return proper 401 responses. Tomorrow I need to finish the deployment work and push the final code to GitHub. I must update the README with setup instructions. Before submitting the form, I should test register, login, note creation, note sharing, search, and the action extraction endpoint.
```

### Success Response

Status code: `200 OK`

```json
{
  "note_id": 3,
  "action_items": [
    "review the authentication flow once more and check whether invalid tokens return proper 401 responses",
    "finish the deployment work and push the final code to GitHub",
    "update the README with setup instructions",
    "test register, login, note creation, note sharing, search, and the action extraction endpoint"
  ]
}
```

### Access Rule

The endpoint can be used if:

- The authenticated user owns the note.
- The note has been shared with the authenticated user.

---

## 12. About

```http
GET /about
```

### Success Response

Status code: `200 OK`

```json
{
  "name": "Your Name",
  "email": "your-email@example.com",
  "my features": {
    "Smart Action Item Extraction": "Added GET /notes/{id}/actions to extract possible tasks from a note using lightweight NLP-style rules. I chose this because notes often contain hidden todos, and turning them into action items makes the app more useful and productivity-focused.",
    "Search notes": "Added GET /search?q=keyword so users can quickly find notes by title or content."
  }
}
```

---

## 13. OpenAPI JSON

```http
GET /openapi.json
```

FastAPI automatically generates the OpenAPI schema for all exposed endpoints.