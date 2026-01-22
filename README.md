# Connectly API

**Connectly API** is a backend service built with Django and the Django REST Framework (DRF). It provides a RESTful interface for managing **Users** and **Posts**, allowing for the creation and retrieval of data via JSON endpoints.

This project serves as a foundational implementation of CRUD operations, tested and verified using Postman.

---

## 🚀 Features

- **User Management:** Create and retrieve user profiles.
- **Post Management:** Create and retrieve text-based posts linked to specific authors.
- **RESTful Architecture:** Clean URL structure and standard HTTP methods.
- **JSON Support:** Fully supports JSON payloads for requests and responses.
- **Scalable Structure:** Built on Django, ready for extensions like authentication and permissions.

---

## 🛠️ Setup Instructions

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd connectly_project
```

### 2. Create and Activate Virtual Environment
It is recommended to run this project in an isolated environment.

Windows:

```bash
python -m venv env
env\Scripts\activate
```

Mac/Linux:
```bash
python3 -m venv env
source env/bin/activate
```


### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
Initialize the SQLite database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Default Data (Optional)
To test the Post creation immediately, you need an existing User (author). You can create one via the Django shell:

```bash
python manage.py shell
```

Inside the shell, run:
```bash
python
from posts.models import User
```

# Create a default user with ID 1 (or next available ID)
User.objects.get_or_create(username='defaultuser', email='defaultuser@example.com')
exit()

### 6. Run Development Server
```bash
python manage.py runserver
```

Open your browser to
```bash
http://127.0.0.1:8000/.
```

You should see the welcome message:

```bash
"Welcome to Connectly API. Use /posts/users/ or /posts/posts/"
```

# 📡 API Endpoints
## 👤 Users
### Retrieve All Users
#### URL: /posts/users/
#### Method: GET
#### Response:
```bash
json
[
    {"id": 1, "username": "defaultuser", "email": "defaultuser@example.com"},
    {"id": 2, "username": "newuser", "email": "newuser@example.com"}
]
```

### Create a User
#### URL: /posts/users/create/
#### Method: POST
#### Body (JSON):
```bash
json
{
    "username": "john_doe",
    "email": "john@example.com"
}
```

## 📝 Posts
### Retrieve All Posts
#### URL: /posts/posts/
#### Method: GET
#### Response:

```bash
json
 Show full code block 
[
    {
        "id": 1, 
        "title": "First Post", 
        "content": "Hello World", 
        "author": 1
    }
]
```

### Create a Post
#### URL: /posts/posts/create/
#### Method: POST
#### Body (JSON):

```bash
json
{
    "title": "My New Post",
    "content": "This is the content of the post.",
    "author": 1
}
```

#### Note: The author field must be the Integer ID of an existing user.

# 🧪 Testing with Postman
Open Postman and create a new request.
Select Method: Choose GET or POST.
Enter URL: e.g., http://127.0.0.1:8000/posts/posts/create/
Configure POST Body:
Go to the Body tab.
Select raw.
Select JSON from the dropdown menu.
Paste the JSON payload (see examples above).
Send: Click the "Send" button.
Verify: Check for a 200 OK or 201 Created status code.
#### ⚠️ Important: Ensure your POST request URLs end with a trailing slash /. Django's APPEND_SLASH setting may cause 500 errors or redirects if this is missing on POST requests.

# 💡 Project Insights
### Challenges & Solutions
- Author Field Constraint: Creating a post failed initially because the author field is required.
- Solution: Documented the need to create a User first and use their numeric ID in the payload.
- Trailing Slashes: Encountered 500 Internal Server Error on POST requests.
- Solution: Standardized all API calls to include the trailing slash /.
- Root URL 404: The base URL http://127.0.0.1:8000/ initially returned a 404.
- Solution: Added a simple view to handle the root URL and guide users to the correct API paths.

### Learning Points
- Setting up a Django project with Django REST Framework.
- Handling Foreign Key relationships in API payloads (User -> Post).
- Debugging HTTP status codes and validating endpoints with Postman.

# 📂 Repository Structure
``` text
├─ manage.py             Django's command-line utility.
├─ requirements.txt         List of project dependencies.
├─ connectly_project/       Project configuration (settings, urls, wsgi).
├─ posts/                   The main app containing:
    ├─ models.py               Database schemas.
    ├─ views.py                    API logic.
    ├─ urls.py                     Endpoint routing.
    └─ serializers.py              Data conversion logic.
```
