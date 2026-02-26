# Connectly Backend – Social API Platform

Connectly is a Django REST Framework backend powering a social media application. It provides core functionality for user management, posts, comments, likes, and personalized news feeds with token-based authentication.

**Milestone 2 Focus:** Post likes, post-scoped comments, Google OAuth integration, pagination, and news feed retrieval.

---

## Core Features

- **Likes System** – Per-post, per-user likes with duplicate prevention
- **Comments System** – Threaded comments on posts with newest-first ordering
- **Google OAuth Login** – Token exchange for third-party authentication
- **News Feed** – Personalized and global feed endpoints with pagination support
- **Pagination** – Comment and feed queries support configurable page sizes

---

## Architecture

The system follows REST principles with clear separation of concerns:

**Models:** User, Post, Comment, Like entities in SQLite database

**Serializers:** Input validation and API response formatting using Django REST Framework

**Views:** Authentication-protected endpoints with custom permission rules (IsPostAuthor for edit/delete)

**Authentication:** Token-based authentication maintained by TokenAuthentication middleware

**Design Patterns:**
- Factory Pattern: PostFactory enforces post creation logic
- Singleton Pattern: LoggerSingleton provides centralized logging

---

## Included Diagrams

The project documentation includes:
- Entity-Relationship Diagram (User, Post, Comment, Like relationships)
- API Flow Diagram (request/response sequences for CRUD operations)
- Google OAuth Flow Diagram (authentication handshake and token exchange)

---

## API Endpoints

**Users**
- GET /posts/users/
- POST /posts/users/

**Posts**
- GET /posts/posts/
- POST /posts/posts/
- GET /posts/posts/{id}/
- PUT /posts/posts/{id}/
- DELETE /posts/posts/{id}/

**Likes & Comments**
- POST /posts/posts/{id}/like/
- POST /posts/posts/{id}/comment/
- GET /posts/posts/{id}/comments/

**Authentication**
- POST /posts/token-auth/

---

## Diagrams

### 1. Entity-Relationship Diagram (ER)

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    USER ||--o{ LIKE : givers
    POST ||--o{ COMMENT : receives
    POST ||--o{ LIKE : receives

    USER {
        int id PK
        string username UK
        string email UK
        datetime created_at
    }

    POST {
        int id PK
        text content
        int author_id FK
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
```

---

### 2. CRUD Operations Flow

```mermaid
sequenceDiagram
    participant Client as Client/Postman
    participant View as Django View
    participant Serializer as Serializer
    participant Model as Database Model
    participant DB as SQLite DB

    rect rgb(200, 220, 255)
    Note over Client,DB: CREATE - POST /posts/posts/
    Client->>View: POST with post data
    View->>Serializer: Validate request
    Serializer->>View: Return validated data
    View->>Model: Create new Post instance
    Model->>DB: INSERT new record
    DB-->>Model: Confirm creation
    Model-->>View: Return created instance
    View-->>Client: 201 Created with post object
    end

    rect rgb(200, 255, 220)
    Note over Client,DB: READ - GET /posts/posts/
    Client->>View: GET request
    View->>Model: Query all posts
    Model->>DB: SELECT * FROM posts
    DB-->>Model: Return records
    Model-->>View: Return post list
    View-->>Client: 200 OK with posts array
    end

    rect rgb(255, 240, 200)
    Note over Client,DB: UPDATE - PUT /posts/posts/{id}/
    Client->>View: PUT with updated data
    View->>Serializer: Validate request
    Serializer->>View: Return validated data
    View->>Model: Update Post instance
    Model->>DB: UPDATE record
    DB-->>Model: Confirm update
    Model-->>View: Return updated instance
    View-->>Client: 200 OK with updated object
    end

    rect rgb(255, 200, 200)
    Note over Client,DB: DELETE - DELETE /posts/posts/{id}/
    Client->>View: DELETE request
    View->>Model: Delete Post instance
    Model->>DB: DELETE FROM posts WHERE id=?
    DB-->>Model: Confirm deletion
    Model-->>View: Deletion confirmed
    View-->>Client: 204 No Content
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
        Router["URL Router<br/>connectly_project/urls.py"]
        Views["Views<br/>posts/views.py"]
    end

    subgraph Auth["Authentication & Authorization"]
        TokenAuth["TokenAuthentication"]
        Perms["Custom Permissions<br/>IsPostAuthor"]
    end

    subgraph Processing["Data Processing"]
        Serializers["Serializers<br/>posts/serializers.py"]
        Factory["PostFactory<br/>factories/post_factory.py"]
    end

    subgraph Models["Data Models"]
        ModelLayer["User, Post, Comment, Like<br/>posts/models.py"]
    end

    subgraph Utils["Utilities"]
        Logger["LoggerSingleton<br/>singletons/logger_singleton.py"]
        Config["ConfigManager<br/>singletons/config_manager.py"]
    end

    subgraph Storage["Storage"]
        DB["SQLite Database<br/>db.sqlite3"]
    end

    Postman -->|HTTP Request| Router
    Router -->|Route| Views
    Views -->|Check Auth| TokenAuth
    Views -->|Check Permission| Perms
    Views -->|Validate Data| Serializers
    Views -->|Create Posts| Factory
    Factory -->|Interact| ModelLayer
    Serializers -->|Interact| ModelLayer
    ModelLayer -->|Query/Persist| DB
    Views -->|Log Events| Logger
    Logger -->|Read Config| Config
    Views -->|Response| Postman

    style Client fill:#e1f5ff
    style API fill:#f3e5f5
    style Auth fill:#fff3e0
    style Processing fill:#e8f5e9
    style Models fill:#fce4ec
    style Utils fill:#f1f8e9
    style Storage fill:#ede7f6
```

---

### 4. API Request/Response Flow

```mermaid
sequenceDiagram
    participant Client as Client
    participant Endpoint as API Endpoint
    participant Auth as Authentication
    participant Perms as Permissions
    participant Handler as Request Handler
    participant Serializer as Serializer
    participant Model as Model
    participant DB as Database

    Client->>Endpoint: HTTP Request + Token
    Note over Endpoint: Route to view method

    Endpoint->>Auth: Validate Token
    alt Token Invalid
        Auth-->>Client: 401 Unauthorized
    else Token Valid
        Auth->>Endpoint: User object
        Endpoint->>Perms: Check Permissions (IsAuthenticated, IsPostAuthor)
        
        alt Permission Denied
            Perms-->>Client: 403 Forbidden
        else Permission Granted
            Perms->>Handler: Proceed to handler
            Handler->>Serializer: Validate input data
            
            alt Validation Fails
                Serializer-->>Client: 400 Bad Request {error}
            else Validation Passes
                Serializer->>Handler: Validated data
                Handler->>Model: Process business logic
                Model->>DB: Query/Insert/Update/Delete
                DB-->>Model: Result
                Model->>Handler: Result object
                Handler->>Serializer: Prepare response
                Serializer-->>Client: 200/201/204 with data
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
    participant Google as Google OAuth Server
    participant DB as Database

    User->>Client: Click "Login with Google"
    Client->>Google: Redirect to Google login
    Google->>User: Show consent screen
    User->>Google: Approve permissions
    Google-->>Client: Authorization code + redirect
    Client->>API: POST /posts/oauth/google-token/<br/>{ "code": "...", "id_token": "..." }
    
    API->>Google: Verify ID token signature
    alt Token Invalid
        Google-->>API: Invalid signature
        API-->>Client: 401 Unauthorized
    else Token Valid
        Google-->>API: Token claims (email, name, sub)
        API->>DB: Check if user exists by email
        
        alt User Exists
            DB-->>API: Return existing user
            API->>API: Generate/retrieve token
        else New User
            API->>DB: Create new user with email
            DB-->>API: Return new user
            API->>API: Generate token
        end
        
        API-->>Client: 200 OK { "token": "...", "user": {...} }
        Client->>Client: Store token in local storage
        Client->>API: All future requests with Authorization: Token ...
    end
```

---

## AI Disclosure

This project utilized AI for:
- Troubleshooting and debugging guidance
- Architecture and design pattern clarification
- Documentation review and validation


---

## Development Tools

- **VS Code** – Primary development environment
- **Postman** - API test environment
- **Prettier** – Code formatting (Built-in VSC Extension in device)
- **Better Comments** – Enhanced code annotation and documentation (Built-in VSC Extension in device)
- **Mermaid Extension** - Enhanced diagrams translated into mermaid code

---

## Testing Summary

- **Postman Collection** – Comprehensive API testing with manual verification of all endpoints
- **OAuth Verification** – Tested Google token exchange and user profile retrieval
- **Pagination Validation** – Confirmed page size, count, and navigation parameters work correctly
- **Permission Testing** – Verified author-only access control and 403 error handling

---

## Setup Instructions

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

## Contributors

| Name                  | Role        |
| --------------------- | ----------- |
| Camille Rose Umali    | Contributor |
| Shakira Angela Casusi | Contributor/Documenter/Tester |

Roles inferred from commit history in repository.

