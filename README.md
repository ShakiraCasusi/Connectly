# Connectly API

Connectly is a Django REST Framework backend for a social media platform. It supports account registration, token-based authentication, post publishing with privacy controls, comments, likes, personalized feeds, and Google OAuth login.

**Current milestone scope:** Token-auth-compatible user onboarding, role-aware permissions, post privacy filtering, feed filtering (`global` vs `following`), and Google OAuth token exchange.

---

## Core Features

- **Dual user provisioning** – Registration creates both a Django auth user (for DRF token auth) and a domain profile (`posts.User`)
- **Token Authentication** – DRF `TokenAuthentication` across protected endpoints
- **Posts with Privacy Controls** – Public/private posts with privacy-aware retrieval rules
- **Role-Aware Authorization** – Author-only post edits and admin-only post/comment deletion operations
- **Likes System** – Per-user, per-post likes with duplicate-like prevention
- **Comments System** – Global and post-scoped comments with validation and pagination
- **Feed Retrieval** – Global feed and `following`-filtered feed variants with pagination
- **Google OAuth Login** – Accepts Google `id_token`, verifies it, and returns API token

---

## Architecture

The system follows REST conventions with modular app boundaries and explicit auth/permission layers.

**Models:**
- `posts.User` (domain profile with role)
- `posts.Post` (content + privacy)
- `posts.Comment`
- `posts.Like` (unique user/post pair)
- `posts.Follow` (follower/followed relationship)

**Serializers:**
- Dedicated serializers for user registration/listing, post payloads, comments, and likes
- Input validation for non-empty comment content and registration constraints

**Views:**
- APIViews for users, posts, comments, likes, post-scoped comments, feed retrieval, and OAuth login
- Method-specific permission handling (`GET`/`PUT`/`DELETE`) on post detail operations

**Authentication:**
- DRF `TokenAuthentication` default
- Public registration and Google login endpoints

**Authorization Rules:**
- `IsAuthenticated` baseline for protected routes
- `IsPostAuthor` for post updates
- `IsAdmin` for admin-only destructive actions

**Design Patterns in Codebase:**
- Factory Pattern: `PostFactory` centralizes post object construction
- Singleton Pattern: `LoggerSingleton` and `ConfigManager` utilities

---

## Included Diagrams

The documentation includes:
- Entity-Relationship Diagram (User, Follow, Post, Comment, Like)
- CRUD + Permission Flow Diagram (token auth + per-method permissions)
- System Architecture Diagram (routing, auth, permissions, serializer/model layers)
- API Request/Response Flow (validation and error branches)
- Google OAuth Flow Diagram (token verification and user/token provisioning)

---

## API Endpoints

Base prefix: `/posts/`

**Public / Authentication**
- `POST /posts/users/` – register user (creates auth + domain user)
- `POST /posts/token-auth/` – obtain DRF token (username/password)
- `POST /posts/auth/google/` – exchange Google `id_token` for API token

**Users**
- `GET /posts/users/` – list domain users (auth required)

**Posts**
- `GET /posts/posts/` – list posts
- `POST /posts/posts/` – create post
- `GET /posts/posts/{id}/` – retrieve post (privacy-aware)
- `PUT /posts/posts/{id}/` – update post (author-only)
- `DELETE /posts/posts/{id}/` – delete post (admin-only)

**Comments / Likes**
- `GET /posts/comments/` – list all comments
- `POST /posts/comments/` – create global comment payload (`post` required)
- `POST /posts/posts/{id}/like/` – like post
- `POST /posts/posts/{id}/comment/` – add comment to post using `{ "content": "..." }`
- `GET /posts/posts/{id}/comments/` – paginated post comments (newest-first)

**Feed / Diagnostics**
- `GET /posts/feed/` – paginated global feed
- `GET /posts/feed/?filter=following` – feed from followed users only
- `GET /posts/test-auth/` – token authentication debug endpoint

---

## Diagrams

### 1. Entity-Relationship Diagram (ER)

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    USER ||--o{ LIKE : gives
    USER ||--o{ FOLLOW : follower
    USER ||--o{ FOLLOW : followed
    POST ||--o{ COMMENT : receives
    POST ||--o{ LIKE : receives

    USER {
        int id PK
        string username UK
        string email UK
        string role "admin|user|guest"
        datetime created_at
    }

    POST {
        int id PK
        text content
        int author_id FK
        string privacy "public|private"
        datetime created_at
    }

    COMMENT {
        int id PK
        text text
        int author_id FK
        int post_id FK
        datetime created_at
    }

    LIKE {
        int id PK
        int user_id FK
        int post_id FK
        datetime created_at
        string unique_constraint "user_id, post_id"
    }

    FOLLOW {
        int id PK
        int follower_id FK
        int followed_id FK
        datetime created_at
        string unique_together "follower_id, followed_id"
    }
```

---

### 2. CRUD + Permission Operations Flow

```mermaid
sequenceDiagram
    participant Client as Client/Postman
    participant View as Django APIView
    participant Auth as TokenAuthentication
    participant Perm as Permission Class
    participant Serializer as Serializer
    participant Model as Model Layer
    participant DB as SQLite

    rect rgb(200, 220, 255)
    Note over Client,DB: CREATE - POST /posts/posts/
    Client->>View: POST + Token + payload
    View->>Auth: Validate token
    Auth-->>View: Authenticated user
    View->>Serializer: Validate payload
    Serializer-->>View: Validated data
    View->>Model: Build post via PostFactory + assign author/privacy
    Model->>DB: INSERT post
    DB-->>Model: Created row
    View-->>Client: 201 Created
    end

    rect rgb(200, 255, 220)
    Note over Client,DB: READ - GET /posts/posts/{id}/
    Client->>View: GET + Token
    View->>Auth: Validate token
    Auth-->>View: Authenticated user
    View->>Perm: Apply privacy rule (private visible to owner only)
    alt Not allowed
        Perm-->>Client: 403 Forbidden
    else Allowed
        View->>Model: Fetch post
        Model->>DB: SELECT by id
        DB-->>Model: Row
        View-->>Client: 200 OK
    end
    end

    rect rgb(255, 240, 200)
    Note over Client,DB: UPDATE - PUT /posts/posts/{id}/
    Client->>View: PUT + Token + payload
    View->>Auth: Validate token
    Auth-->>View: Authenticated user
    View->>Perm: IsPostAuthor?
    alt Not author
        Perm-->>Client: 403 Forbidden
    else Author
        View->>Serializer: Validate updates
        Serializer-->>View: Validated data
        View->>DB: UPDATE post
        DB-->>View: Updated row
        View-->>Client: 200 OK
    end
    end

    rect rgb(255, 200, 200)
    Note over Client,DB: DELETE - DELETE /posts/posts/{id}/
    Client->>View: DELETE + Token
    View->>Auth: Validate token
    Auth-->>View: Authenticated user
    View->>Perm: IsAdmin?
    alt Not admin
        Perm-->>Client: 403 Forbidden
    else Admin
        View->>DB: DELETE row
        DB-->>View: Deletion confirmed
        View-->>Client: 204 No Content
    end
    end
```

---

### 3. System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Postman["Postman / Frontend Client"]
    end

    subgraph API["API Layer"]
        Router["URL Router<br/>connectly_project/urls.py + posts/urls.py"]
        Views["Views<br/>posts/views.py"]
    end

    subgraph Auth["Authentication & Authorization"]
        TokenAuth["TokenAuthentication"]
        Perms["Permissions<br/>IsAuthenticated / IsPostAuthor / IsAdmin"]
    end

    subgraph Processing["Data Processing"]
        Serializers["Serializers<br/>posts/serializers.py"]
        Factory["PostFactory<br/>factories/post_factory.py"]
    end

    subgraph Domain["Domain Model Layer"]
        DomainModels["User, Post, Comment, Like, Follow<br/>posts/models.py"]
    end

    subgraph Identity["Identity Layer"]
        DjangoAuth["django.contrib.auth User"]
        TokenModel["rest_framework.authtoken.Token"]
    end

    subgraph Utils["Utilities"]
        Logger["LoggerSingleton"]
        Config["ConfigManager"]
    end

    subgraph Storage["Storage"]
        DB["SQLite Database<br/>db.sqlite3"]
    end

    Postman -->|HTTP Request| Router
    Router -->|Route| Views
    Views -->|Authenticate| TokenAuth
    Views -->|Authorize| Perms
    Views -->|Validate| Serializers
    Views -->|Create Post Object| Factory
    Serializers -->|Read/Write| DomainModels
    Factory -->|Build unsaved Post| DomainModels
    Views -->|Create/Login Users| DjangoAuth
    Views -->|Issue API Tokens| TokenModel
    DomainModels -->|Persist| DB
    DjangoAuth -->|Persist| DB
    TokenModel -->|Persist| DB
    Views -->|Log Events| Logger
    Logger -->|Read Config| Config
    Views -->|HTTP Response| Postman
```

---

### 4. API Request/Response Flow

```mermaid
sequenceDiagram
    participant Client as Client
    participant Endpoint as API Endpoint
    participant Auth as Authentication
    participant Perms as Permissions
    participant Serializer as Serializer
    participant Model as Model/Service
    participant DB as Database

    Client->>Endpoint: HTTP Request (+ Token if protected)
    Endpoint->>Auth: Validate token/session context

    alt Auth failed
        Auth-->>Client: 401 Unauthorized
    else Auth success
        Endpoint->>Perms: Check endpoint/method permissions

        alt Permission denied
            Perms-->>Client: 403 Forbidden
        else Permission granted
            Endpoint->>Serializer: Validate request payload

            alt Validation fails
                Serializer-->>Client: 400 Bad Request
            else Validation passes
                Endpoint->>Model: Execute business logic
                Model->>DB: Query/Insert/Update/Delete

                alt Resource missing
                    DB-->>Endpoint: Not found
                    Endpoint-->>Client: 404 Not Found
                else Success
                    DB-->>Model: Result
                    Model-->>Endpoint: Domain object/data
                    Endpoint-->>Client: 200/201/204 Success Response
                end
            end
        end
    end
```

---

### 5. Google OAuth Authentication Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Client as Frontend Client
    participant API as Connectly API
    participant Google as Google OAuth
    participant AuthDB as Django Auth User
    participant DomainDB as posts.User
    participant TokenDB as DRF Token

    User->>Client: Click "Login with Google"
    Client->>Google: Google Sign-In flow
    Google-->>Client: id_token
    Client->>API: POST /posts/auth/google/ { "id_token": "..." }

    API->>Google: verify_oauth2_token(id_token, GOOGLE_CLIENT_ID)
    alt Invalid token
        Google-->>API: Verification error
        API-->>Client: 400 Token verification failed
    else Valid token
        Google-->>API: Verified claims (email, profile)
        API->>AuthDB: Get or create auth user by email
        AuthDB-->>API: Auth user instance

        API->>DomainDB: Get or create domain user (username/email)
        DomainDB-->>API: Domain profile

        API->>TokenDB: Get or create DRF token for auth user
        TokenDB-->>API: API token

        API-->>Client: 200 {token, user_id, username, email}
        Client->>Client: Store token
        Client->>API: Use Authorization: Token <token> on protected calls
    end
```

---

## AI Disclosure

This project may use AI assistance for:
- troubleshooting and debugging support
- architecture/design clarification
- documentation drafting and refinement

---

## Development Tools

- **Python + Django** – Core backend framework
- **Django REST Framework** – API serialization, auth, response handling
- **SQLite** – Default local development database
- **Postman** – Manual API endpoint verification
- **Mermaid** – Architecture and flow documentation diagrams

---

## Testing Summary

- **Automated API tests (`posts/tests.py`)**
  - Likes and post-scoped comments behavior
  - Google OAuth endpoint logic (mocked Google verification)
  - Feed behavior for global vs `following` filter
- **Permission coverage**
  - Author-only and admin-only guards tested via API behavior
- **Pagination checks**
  - Comment and feed endpoints validate paginated responses

---

## Setup Instructions

**1) Clone the repository:**

```bash
git clone <repository-url>
cd Connectly/connectly_project
```

**2) Create and activate virtual environment:**

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3) Install dependencies:**

```bash
pip install -r requirements.txt
```

**4) Run migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

**5) Start development server:**

```bash
python manage.py runserver
```

**Default server URL:**

```text
http://127.0.0.1:8000/
```

---

## Contributors

| Name                  | Role                          |
| --------------------- | ----------------------------- |
| Camille Rose Umali    | Contributor                   |
| Shakira Angela Casusi | Contributor / Documenter / QA |

Roles inferred from project history and documentation context.
