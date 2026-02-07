# Connectly API Documentation

**Connectly API** is a backend service built with Django and Django REST Framework. The API exposes REST endpoints for **Users**, **Posts**, and **Comments**. All endpoints use JSON. Token authentication protects resources. Object-level permissions restrict post updates and deletes.

---

## 1. Overview

Connectly provides a RESTful backend for basic social features.

**Primary scope**:
- Users
- Posts
- Comments

**Key goals**:
- Clean REST design
- Token-based authentication
- Author-only access control
- Clear separation of concerns
- Demonstration of design patterns

The API is tested using Postman.

---

## 2. Features

- User creation and listing
- Post CRUD operations
- Comment creation and listing
- Token authentication using DRF
- Author-only permissions for post updates and deletes
- Structured logging
- Factory and Singleton patterns

---

## 3. System Architecture

**Core framework**:
- Django
- Django REST Framework

**Project structure**:
- connectly_project/  
  Project settings and root URLs

- posts/  
  Main application

**Key files**:
- posts/models.py  
  User, Post, Comment models

- posts/serializers.py  
  API input and output validation

- posts/views.py  
  API views with auth and permissions

- posts/permissions.py  
  Custom access rules

- factories/post_factory.py  
  Factory pattern for post creation

- singletons/logger_singleton.py  
  Shared logger instance

---

## 4. Data Model

**User:**
- username (unique)
- email (unique)
- created_at

**Post:**
- content
- author (foreign key to User)
- created_at

**Comment:**
- text
- author (foreign key to User)
- post (foreign key to Post)
- created_at

---

## 5. Setup Instructions

**Clone the repository:**

```bash
git clone <repository-url>
cd connectly_project
```

**Create virtual environment:**

**Windows:**

```bash
python -m venv env
env\Scripts\activate
```

**Mac or Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Apply migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

**Run development server:**

```bash
python manage.py runserver
```

**Server runs at:**

```text
http://127.0.0.1:8000/
```

---

## 6. API Reference

**Base path:**

```text
/posts/
```

### 6.1 Users

| Operation   | Method | URL           |
| ----------- | ------ | ------------- |
| List users  | GET    | /posts/users/ |
| Create user | POST   | /posts/users/ |

**Create user payload:**

```json
{
  "username": "jane_doe",
  "email": "jane@example.com"
}
```

---

### 6.2 Posts

| Operation     | Method | URL                | Access |
| ------------- | ------ | ------------------ | ------ |
| List posts    | GET    | /posts/posts/      | Auth   |
| Create post   | POST   | /posts/posts/      | Auth   |
| Retrieve post | GET    | /posts/posts/<id>/ | Author |
| Update post   | PUT    | /posts/posts/<id>/ | Author |
| Delete post   | DELETE | /posts/posts/<id>/ | Author |

**Create post payload:**

```json
{
  "post_type": "text",
  "content": "Hello world",
  "metadata": {}
}
```

**Post response:**

```json
{
  "id": 1,
  "content": "Hello world",
  "author": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "comments": []
}
```

---

### 6.3 Comments

| Operation      | Method | URL              |
| -------------- | ------ | ---------------- |
| List comments  | GET    | /posts/comments/ |
| Create comment | POST   | /posts/comments/ |

**Create comment payload:**

```json
{
  "text": "Nice post!",
  "post": 1
}
```

---

### 6.4 Authentication

| Operation    | Method | URL                |
| ------------ | ------ | ------------------ |
| Obtain token | POST   | /posts/token-auth/ |

**Authorization header:**

```text
Authorization: Token <token>
```

---

## 7. Security and Validation

**Authentication:**

* DRF TokenAuthentication

**Authorization:**

* IsAuthenticated on all endpoints
* IsPostAuthor for post update and delete

**Validation:**

* Serializers validate request data
* PostFactory enforces post-type rules

---

## 8. Design Patterns

**Factory Pattern:**

* PostFactory.create_post handles post creation logic and validation

**Singleton Pattern:**

* LoggerSingleton ensures one shared logger instance

---

## 9. Diagrams

### 9.1 Access Control Diagram
```mermaid
flowchart LR
  subgraph Roles
    User[Authenticated User]
    Author[Post Author]
    Admin[Admin Group Member]
  end

  subgraph Controls
    IsAuth[IsAuthenticated]
    IsPostAuthor[IsPostAuthor]
    IsAdmin[IsAdmin]
  end

  subgraph Resources
    Users[Users API]
    Posts[Posts API]
    Comments[Comments API]
    PostRead[Read Post]
    PostWrite[Update/Delete Post]
    AdminActions[Admin-Only Actions]
  end

  User --> IsAuth
  Author --> IsPostAuthor
  Admin --> IsAdmin

  IsAuth --> Users
  IsAuth --> Posts
  IsAuth --> Comments
  IsAuth --> PostRead
  IsPostAuthor --> PostWrite
  IsAdmin --> AdminActions
```

### 9.2 Authentication Flow Diagram
```mermaid
sequenceDiagram
  participant Client
  participant TokenEndpoint as Token Auth Endpoint
  participant API as Protected API View
  participant Auth as TokenAuthentication
  participant Perms as Permissions

  Client->>TokenEndpoint: POST /posts/token-auth/ (credentials)
  TokenEndpoint-->>Client: 200 OK (token)

  Client->>API: Request with Authorization: Token <token>
  API->>Auth: Validate token
  Auth-->>API: user
  API->>Perms: Check IsAuthenticated / IsPostAuthor
  Perms-->>API: allow/deny
  API-->>Client: 200 OK (resource) or 403 Forbidden
```


### 9.3 System Architecture Diagram
```mermaid
flowchart TB
  Client[Client / Postman]
  API[Django + DRF API]
  Auth[TokenAuthentication]
  Perms[Custom Permissions]
  Ser[Serializers]
  Models[(Models)]
  Logger[LoggerSingleton]
  Factory[PostFactory]
  DB[(SQLite DB)]

  Client --> API
  API --> Auth
  API --> Perms
  API --> Ser
  Ser --> Models
  Models --> DB
  API --> Logger
  API --> Factory
  Factory --> Models
```

### 9.4 CRUD Diagram
```mermaid
sequenceDiagram
  participant C as Client
  participant V as Posts API View
  participant S as Serializer
  participant M as Model

  C->>V: Create (POST /posts/posts/)
  V->>S: Validate input
  S-->>V: Validated data
  V->>M: Create record
  M-->>V: Created
  V-->>C: 201 Created

  C->>V: Read List (GET /posts/posts/)
  V->>M: Query list
  M-->>V: Results
  V-->>C: 200 OK

  C->>V: Read Detail (GET /posts/posts/{id}/)
  V->>M: Query record
  M-->>V: Record
  V-->>C: 200 OK

  C->>V: Update (PUT /posts/posts/{id}/)
  V->>S: Validate input
  S-->>V: Validated data
  V->>M: Update record
  M-->>V: Updated
  V-->>C: 200 OK

  C->>V: Delete (DELETE /posts/posts/{id}/)
  V->>M: Delete record
  M-->>V: Deleted
  V-->>C: 204 No Content
```

---

## 10. Troubleshooting

**401 Unauthorized:**

* Missing or invalid token

**403 Forbidden:**

* You are not the post author

**400 Bad Request:**

* PostFactory validation failed
* post_type or metadata mismatch

**Token issues:**

* Check token-auth endpoint setup
* Confirm correct user model

---

## 11. Example Request

```bash
curl -X POST http://127.0.0.1:8000/posts/posts/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"post_type":"text","content":"Hello","metadata":{}}'
```

---

## 12. Contributors

| Name                  | Role        |
| --------------------- | ----------- |
| Camille Rose          | Contributor |
| Shakira Angela Casusi | Contributor/Documenter |

Roles inferred from commit history in repository.

