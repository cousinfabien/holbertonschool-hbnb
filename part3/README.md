# HBnB Evolution — Part 3

A RESTful API built with Flask, SQLAlchemy, and JWT authentication.
This is Part 3 of the HBnB Evolution project — it extends the Part 2 prototype with real database persistence, authentication, and role-based access control.

---

## Authors

- **Julian** — App Factory, RBAC, SQL Scripts, ER Diagrams, Tests
- **Fabien** — JWT Authentication, Login Endpoint
- **Georgia** — SQLAlchemy Repository, Model Mapping, Relationships

---

## What's New in Part 3

| Feature | Description |
|---|---|
| 🔐 JWT Authentication | Login endpoint returns a signed token |
| 🛡️ RBAC | Admins have elevated permissions |
| 🗄️ SQLAlchemy | Data persists in SQLite (dev) or MySQL (prod) |
| 🔗 Relationships | Foreign keys and many-to-many between entities |
| 📜 SQL Scripts | Raw SQL for schema creation and initial data |
| 📊 ER Diagram | Mermaid.js diagram of the database schema |

---

## Architecture

```
part3/
├── app/
│   ├── __init__.py          # Application Factory (create_app)
│   ├── extensions.py        # db, bcrypt, jwt instances
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py      # POST /api/v1/auth/login
│   │       ├── users.py     # CRUD /api/v1/users/
│   │       ├── places.py    # CRUD /api/v1/places/
│   │       ├── reviews.py   # CRUD /api/v1/reviews/
│   │       └── amenities.py # CRUD /api/v1/amenities/
│   ├── models/
│   │   ├── base_model.py    # SQLAlchemy base with id, created_at, updated_at
│   │   ├── user.py          # User model + bcrypt
│   │   ├── place.py         # Place model + place_amenity table
│   │   ├── review.py        # Review model
│   │   └── amenity.py       # Amenity model
│   ├── persistence/
│   │   ├── repository.py    # InMemoryRepository + SQLAlchemyRepository
│   │   └── user_repository.py # UserRepository with get_user_by_email
│   ├── services/
│   │   └── facade.py        # HBnBFacade — connects API to persistence
│   └── tests/
│       └── test_part3.py    # Full test suite (61 tests)
├── scripts/
│   ├── create_tables.sql    # SQL schema creation
│   └── initial_data.sql     # Admin user + amenities
├── config.py                # Dev / Testing / Production configs
├── run.py                   # Entry point
└── ERD.md                   # Entity Relationship Diagram
```

### Layer Architecture

```
Presentation (API)
      │
      ▼
Business Logic (Facade)
      │
      ▼
Persistence (SQLAlchemyRepository)
      │
      ▼
Database (SQLite / MySQL)
```

---

## Installation

**1. Clone the repository:**
```bash
git clone https://github.com/juliangf94/holbertonschool-hbnb.git
cd holbertonschool-hbnb/part3
```

**2. Create and activate virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Create environment file:**
```bash
cp .env.example .env
```

**5. Run the application:**
```bash
python3 run.py
```

The API will be available at `http://127.0.0.1:5000/api/v1/`

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Login and get JWT token | Public |

### Users
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/users/` | Create a user | Admin only |
| GET | `/api/v1/users/` | List all users | Public |
| GET | `/api/v1/users/<id>` | Get user by ID | Public |
| PUT | `/api/v1/users/<id>` | Update user | Owner / Admin |

### Places
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/places/` | Create a place | Authenticated |
| GET | `/api/v1/places/` | List all places | Public |
| GET | `/api/v1/places/<id>` | Get place by ID | Public |
| PUT | `/api/v1/places/<id>` | Update place | Owner / Admin |
| GET | `/api/v1/places/<id>/reviews` | Get reviews for a place | Public |

### Reviews
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/reviews/` | Create a review | Authenticated |
| GET | `/api/v1/reviews/` | List all reviews | Public |
| GET | `/api/v1/reviews/<id>` | Get review by ID | Public |
| PUT | `/api/v1/reviews/<id>` | Update review | Author / Admin |
| DELETE | `/api/v1/reviews/<id>` | Delete review | Author / Admin |

### Amenities
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/amenities/` | Create amenity | Admin only |
| GET | `/api/v1/amenities/` | List all amenities | Public |
| GET | `/api/v1/amenities/<id>` | Get amenity by ID | Public |
| PUT | `/api/v1/amenities/<id>` | Update amenity | Admin only |

---

## Authentication

The API uses JWT (JSON Web Tokens). To access protected endpoints:

**1. Login:**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hbnb.io", "password": "admin1234"}'
```

**2. Use the token:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/users/" \
  -H "Authorization: Bearer <your_token>"
```

---

## Database

The application uses **SQLite** in development and can be configured for **MySQL** in production.

**Initialize with SQL scripts:**
```bash
sqlite3 instance/development.db < scripts/create_tables.sql
sqlite3 instance/development.db < scripts/initial_data.sql
```

**Default admin credentials:**
- Email: `admin@hbnb.io`
- Password: `admin1234`

---

## Running Tests

```bash
cd part3
source .venv/bin/activate
python -m pytest app/tests/test_part3.py -v
```

The test suite covers all 10 tasks:
- App Factory Configuration
- Password Hashing
- JWT Authentication
- Authenticated Endpoints
- RBAC (Role-Based Access Control)
- SQLAlchemy Repository
- Entity Mapping
- Relationships
- SQL Scripts
- ER Diagram

---

## Swagger UI

Interactive API documentation available at:
```
http://127.0.0.1:5000/api/v1/
```

Click the 🔓 **Authorize** button and paste your JWT token to test protected endpoints directly from the browser.

---

## ER Diagram

See [ERD.md](./ERD.md) for the full entity relationship diagram.
