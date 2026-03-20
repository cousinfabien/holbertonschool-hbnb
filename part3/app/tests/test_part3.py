#!/usr/bin/python3
"""
HBnB Part 3 — Full Test Suite
Tests cover Tasks 0-10: App Factory, Auth, JWT, RBAC, SQLAlchemy, Relationships, SQL Scripts
"""
import pytest
import json
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
import config as app_config


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture(scope='session')
def app():
    """Create application for testing using TestingConfig."""
    app = create_app(app_config.TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def admin_token(client):
    """Get admin JWT token."""
    # Create admin user directly in DB
    with client.application.app_context():
        admin = User(
            first_name="Admin",
            last_name="Test",
            email="admin@test.com",
            password="temp",
            is_admin=True
        )
        admin.hash_password("admin1234")
        _db.session.add(admin)
        _db.session.commit()

    response = client.post('/api/v1/auth/login',
        data=json.dumps({'email': 'admin@test.com', 'password': 'admin1234'}),
        content_type='application/json')
    return json.loads(response.data)['access_token']


@pytest.fixture(scope='session')
def user_token(client, admin_token):
    """Create a regular user and get their token."""
    client.post('/api/v1/users/',
        data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password': 'password123'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {admin_token}'})

    response = client.post('/api/v1/auth/login',
        data=json.dumps({'email': 'john@test.com', 'password': 'password123'}),
        content_type='application/json')
    return json.loads(response.data)['access_token']


# ================================================================
# TASK 0 — App Factory Configuration
# ================================================================

class TestAppFactory:

    def test_create_app_accepts_config_class(self):
        """create_app() accepts a config_class parameter."""
        app = create_app(app_config.DevelopmentConfig)
        assert app is not None

    def test_default_config_is_development(self):
        """Default config_class is DevelopmentConfig."""
        app = create_app()
        assert app.config['DEBUG'] is True

    def test_app_config_from_object(self):
        """App is configured using app.config.from_object()."""
        app = create_app(app_config.DevelopmentConfig)
        assert 'SQLALCHEMY_DATABASE_URI' in app.config

    def test_create_app_returns_flask_app(self):
        """create_app() returns a Flask app instance."""
        from flask import Flask
        app = create_app()
        assert isinstance(app, Flask)

    def test_testing_config(self):
        """App can be started with TestingConfig."""
        app = create_app(app_config.TestingConfig)
        assert app.config['TESTING'] is True

    def test_production_config(self):
        """App can be started with ProductionConfig."""
        app = create_app(app_config.ProductionConfig)
        assert app.config['DEBUG'] is False


# ================================================================
# TASK 1 — Password Hashing (Flask-Bcrypt)
# ================================================================

class TestPasswordHashing:

    def test_flask_bcrypt_installed(self):
        """flask-bcrypt is installed."""
        import flask_bcrypt
        assert flask_bcrypt is not None

    def test_password_is_hashed_on_create(self, client, admin_token):
        """Password is stored as bcrypt hash, not plain text."""
        response = client.post('/api/v1/users/',
            data=json.dumps({
                'first_name': 'Hash',
                'last_name': 'Test',
                'email': 'hash@test.com',
                'password': 'plaintext123'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'password' not in data

    def test_password_not_returned_in_response(self, client, admin_token):
        """Password field is never returned in API responses."""
        response = client.get('/api/v1/users/',
            headers={'Authorization': f'Bearer {admin_token}'})
        users = json.loads(response.data)
        for user in users:
            assert 'password' not in user

    def test_hash_password_method(self, app):
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="Hash",
                email="hashtest@test.com",
                password="temp",
                is_admin=False
            )
            user.hash_password("testpass")
            assert user.password.startswith('$2b$')

    def test_verify_password_method(self, app):
        """User.verify_password() returns True for correct password."""
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="Verify",
                email="verifytest@test.com",
                password="temp",
                is_admin=False
            )
            user.hash_password("testpass")
            assert user.verify_password("testpass") is True
            assert user.verify_password("wrongpass") is False


# ================================================================
# TASK 2 — JWT Authentication
# ================================================================

class TestJWTAuthentication:

    def test_flask_jwt_extended_installed(self):
        """flask-jwt-extended is installed."""
        import flask_jwt_extended
        assert flask_jwt_extended is not None

    def test_login_returns_token(self, client):
        """POST /api/v1/auth/login returns access_token."""
        response = client.post('/api/v1/auth/login',
            data=json.dumps({'email': 'admin@test.com', 'password': 'admin1234'}),
            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data

    def test_login_invalid_credentials(self, client):
        """POST /api/v1/auth/login returns 401 for wrong password."""
        response = client.post('/api/v1/auth/login',
            data=json.dumps({'email': 'admin@test.com', 'password': 'wrongpassword'}),
            content_type='application/json')
        assert response.status_code == 401

    def test_login_unknown_email(self, client):
        """POST /api/v1/auth/login returns 401 for unknown email."""
        response = client.post('/api/v1/auth/login',
            data=json.dumps({'email': 'unknown@test.com', 'password': 'password'}),
            content_type='application/json')
        assert response.status_code == 401

    def test_protected_endpoint_requires_token(self, client):
        """Protected endpoints return 401 without token."""
        response = client.post('/api/v1/users/',
            data=json.dumps({
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'notoken@test.com',
                'password': 'password'
            }),
            content_type='application/json')
        assert response.status_code == 401

    def test_token_contains_is_admin_claim(self, client):
        """JWT token contains is_admin claim."""
        response = client.post('/api/v1/auth/login',
            data=json.dumps({'email': 'admin@test.com', 'password': 'admin1234'}),
            content_type='application/json')
        token = json.loads(response.data)['access_token']
        # Decode payload (middle part of JWT)
        import base64
        payload = token.split('.')[1]
        # Add padding
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload))
        assert 'is_admin' in decoded
        assert decoded['is_admin'] is True


# ================================================================
# TASK 3 — Authenticated Endpoints
# ================================================================

class TestAuthenticatedEndpoints:

    def test_create_place_requires_token(self, client):
        """POST /api/v1/places/ returns 401 without token."""
        response = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'Test Place',
                'price': 100.0,
                'latitude': 48.8566,
                'longitude': 2.3522
            }),
            content_type='application/json')
        assert response.status_code == 401

    def test_create_place_with_token(self, client, user_token):
        """POST /api/v1/places/ succeeds with valid token."""
        response = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'Test Place',
                'price': 100.0,
                'latitude': 48.8566,
                'longitude': 2.3522
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert response.status_code == 201

    def test_owner_id_forced_from_token(self, client, user_token):
        """owner_id is always set from JWT token, not from request body."""
        response = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'Owner Test Place',
                'price': 50.0,
                'latitude': 10.0,
                'longitude': 10.0,
                'owner_id': 'fake-owner-id'  # should be ignored
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['owner_id'] != 'fake-owner-id'

    def test_get_places_is_public(self, client):
        """GET /api/v1/places/ is accessible without token."""
        response = client.get('/api/v1/places/')
        assert response.status_code == 200

    def test_get_users_is_public(self, client):
        """GET /api/v1/users/ is accessible without token."""
        response = client.get('/api/v1/users/')
        assert response.status_code == 200

    def test_get_amenities_is_public(self, client):
        """GET /api/v1/amenities/ is accessible without token."""
        response = client.get('/api/v1/amenities/')
        assert response.status_code == 200


# ================================================================
# TASK 4 — RBAC (Role-Based Access Control)
# ================================================================

class TestRBAC:

    def test_create_user_requires_admin(self, client, user_token):
        """POST /api/v1/users/ returns 403 for non-admin."""
        response = client.post('/api/v1/users/',
            data=json.dumps({
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'rbac@test.com',
                'password': 'password'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert response.status_code == 403

    def test_create_user_as_admin(self, client, admin_token):
        """POST /api/v1/users/ succeeds for admin."""
        response = client.post('/api/v1/users/',
            data=json.dumps({
                'first_name': 'RBAC',
                'last_name': 'User',
                'email': 'rbacadmin@test.com',
                'password': 'password'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 201

    def test_create_amenity_requires_admin(self, client, user_token):
        """POST /api/v1/amenities/ returns 403 for non-admin."""
        response = client.post('/api/v1/amenities/',
            data=json.dumps({'name': 'TestAmenity'}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert response.status_code == 403

    def test_create_amenity_as_admin(self, client, admin_token):
        """POST /api/v1/amenities/ succeeds for admin."""
        response = client.post('/api/v1/amenities/',
            data=json.dumps({'name': 'WiFi Test'}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 201

    def test_update_place_non_owner_forbidden(self, client, user_token, admin_token):
        """PUT /api/v1/places/<id> returns 403 for non-owner."""
        # Create a place as admin
        r = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'Admin Place',
                'price': 200.0,
                'latitude': 1.0,
                'longitude': 1.0
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        place_id = json.loads(r.data)['id']

        # Try to update as regular user
        response = client.put(f'/api/v1/places/{place_id}',
            data=json.dumps({'title': 'Hacked Title'}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert response.status_code == 403

    def test_admin_bypasses_ownership(self, client, user_token, admin_token):
        """Admin can update any place regardless of ownership."""
        # Create place as regular user
        r = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'User Place',
                'price': 75.0,
                'latitude': 2.0,
                'longitude': 2.0
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        place_id = json.loads(r.data)['id']

        # Admin updates it
        response = client.put(f'/api/v1/places/{place_id}',
            data=json.dumps({'title': 'Admin Updated'}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200


# ================================================================
# TASK 5 — SQLAlchemy Repository
# ================================================================

class TestSQLAlchemyRepository:

    def test_sqlalchemy_installed(self):
        """flask-sqlalchemy is installed."""
        import flask_sqlalchemy
        assert flask_sqlalchemy is not None

    def test_sqlalchemy_repository_exists(self):
        """SQLAlchemyRepository class exists."""
        from app.persistence.repository import SQLAlchemyRepository
        assert SQLAlchemyRepository is not None

    def test_in_memory_repository_still_exists(self):
        """InMemoryRepository still exists for backwards compatibility."""
        from app.persistence.repository import InMemoryRepository
        assert InMemoryRepository is not None

    def test_facade_uses_sqlalchemy_repository(self):
        """Facade uses SQLAlchemyRepository for persistence."""
        from app.services.facade import HBnBFacade
        from app.persistence.repository import SQLAlchemyRepository
        facade = HBnBFacade()
        assert isinstance(facade.place_repo, SQLAlchemyRepository)
        assert isinstance(facade.review_repo, SQLAlchemyRepository)
        assert isinstance(facade.amenity_repo, SQLAlchemyRepository)


# ================================================================
# TASK 6 — User Entity Mapping
# ================================================================

class TestUserEntityMapping:

    def test_base_model_inherits_db_model(self):
        """BaseModel inherits from db.Model."""
        from app.models.base_model import BaseModel
        from app.extensions import db
        assert issubclass(BaseModel, db.Model)

    def test_base_model_is_abstract(self):
        """BaseModel has __abstract__ = True."""
        from app.models.base_model import BaseModel
        assert BaseModel.__abstract__ is True

    def test_user_has_tablename(self):
        """User model has __tablename__ = 'users'."""
        assert User.__tablename__ == 'users'

    def test_user_repository_exists(self):
        """UserRepository class exists."""
        from app.persistence.user_repository import UserRepository
        assert UserRepository is not None

    def test_facade_uses_user_repository(self):
        """Facade uses UserRepository for user operations."""
        from app.services.facade import HBnBFacade
        from app.persistence.user_repository import UserRepository
        facade = HBnBFacade()
        assert isinstance(facade.user_repo, UserRepository)

    def test_user_crud(self, client, admin_token):
        """User CRUD operations work correctly."""
        # Create
        r = client.post('/api/v1/users/',
            data=json.dumps({
                'first_name': 'CRUD',
                'last_name': 'Test',
                'email': 'crud@test.com',
                'password': 'password123'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 201
        user_id = json.loads(r.data)['id']

        # Read
        r = client.get(f'/api/v1/users/{user_id}')
        assert r.status_code == 200


# ================================================================
# TASK 7 — Place, Review, Amenity Mapping
# ================================================================

class TestEntityMapping:

    def test_place_has_tablename(self):
        """Place model has __tablename__ = 'places'."""
        assert Place.__tablename__ == 'places'

    def test_review_has_tablename(self):
        """Review model has __tablename__ = 'reviews'."""
        assert Review.__tablename__ == 'reviews'

    def test_amenity_has_tablename(self):
        """Amenity model has __tablename__ = 'amenities'."""
        assert Amenity.__tablename__ == 'amenities'

    def test_place_crud(self, client, user_token):
        """Place CRUD operations work correctly."""
        r = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'CRUD Place',
                'price': 100.0,
                'latitude': 48.8566,
                'longitude': 2.3522
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert r.status_code == 201
        place_id = json.loads(r.data)['id']

        r = client.get(f'/api/v1/places/{place_id}')
        assert r.status_code == 200

    def test_amenity_crud(self, client, admin_token):
        """Amenity CRUD operations work correctly."""
        r = client.post('/api/v1/amenities/',
            data=json.dumps({'name': 'CRUD Amenity'}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 201


# ================================================================
# TASK 8 — Relationships
# ================================================================

class TestRelationships:

    def test_user_has_places_relationship(self):
        """User model has places relationship."""
        assert hasattr(User, 'places')

    def test_user_has_reviews_relationship(self):
        """User model has reviews relationship."""
        assert hasattr(User, 'reviews')

    def test_place_has_reviews_relationship(self):
        """Place model has reviews relationship."""
        assert hasattr(Place, 'reviews')

    def test_place_has_amenities_relationship(self):
        """Place model has amenities relationship."""
        assert hasattr(Place, 'amenities')

    def test_review_has_foreign_keys(self):
        """Review model has place_id and user_id foreign keys."""
        columns = {c.name for c in Review.__table__.columns}
        assert 'place_id' in columns
        assert 'user_id' in columns

    def test_place_has_owner_id_foreign_key(self):
        """Place model has owner_id foreign key."""
        columns = {c.name for c in Place.__table__.columns}
        assert 'owner_id' in columns

    def test_place_amenity_association_table_exists(self):
        """place_amenity association table exists."""
        from app.models.place import place_amenity
        assert place_amenity is not None

    def test_cannot_review_own_place(self, client, user_token):
        """User cannot review their own place."""
        # Create place
        r = client.post('/api/v1/places/',
            data=json.dumps({
                'title': 'My Place',
                'price': 100.0,
                'latitude': 48.8566,
                'longitude': 2.3522
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        place_id = json.loads(r.data)['id']

        # Try to review own place
        r = client.post('/api/v1/reviews/',
            data=json.dumps({
                'text': 'Great place!',
                'rating': 5,
                'place_id': place_id
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {user_token}'})
        assert r.status_code == 400


# ================================================================
# TASK 9 — SQL Scripts
# ================================================================

class TestSQLScripts:

    def test_create_tables_sql_exists(self):
        """scripts/create_tables.sql file exists."""
        import os
        assert os.path.exists('scripts/create_tables.sql')

    def test_initial_data_sql_exists(self):
        """scripts/initial_data.sql file exists."""
        import os
        assert os.path.exists('scripts/initial_data.sql')

    def test_create_tables_sql_contains_users(self):
        """create_tables.sql contains users table definition."""
        with open('scripts/create_tables.sql', 'r') as f:
            content = f.read()
        assert 'CREATE TABLE' in content.upper()
        assert 'users' in content.lower()

    def test_create_tables_sql_contains_foreign_keys(self):
        """create_tables.sql contains FOREIGN KEY constraints."""
        with open('scripts/create_tables.sql', 'r') as f:
            content = f.read()
        assert 'FOREIGN KEY' in content.upper()

    def test_initial_data_sql_contains_admin(self):
        """insert_initial_data.sql contains admin user insertion."""
        import os
        # Check both possible filenames
        filename = 'scripts/initial_data.sql'
        if not os.path.exists(filename):
            filename = 'scripts/insert_initial_data.sql'
        with open(filename, 'r') as f:
            content = f.read()
        assert 'INSERT' in content.upper()
        assert 'admin' in content.lower()

    def test_initial_data_sql_contains_amenities(self):
        """initial_data.sql contains amenity insertions."""
        import os
        filename = 'scripts/initial_data.sql'
        if not os.path.exists(filename):
            filename = 'scripts/insert_initial_data.sql'
        with open(filename, 'r') as f:
            content = f.read()
        assert 'WiFi' in content or 'wifi' in content.lower()


# ================================================================
# TASK 10 — ER Diagram
# ================================================================

class TestERDiagram:

    def test_erd_file_exists(self):
        """ERD.md or similar file exists."""
        import os
        possible_files = ['ERD.md', 'erd.md', 'diagrams/ERD.md', 'docs/ERD.md']
        found = any(os.path.exists(f) for f in possible_files)
        assert found, "No ERD file found. Create ERD.md with Mermaid.js diagram."

    def test_erd_contains_mermaid_syntax(self):
        """ERD file contains Mermaid.js erDiagram syntax."""
        import os
        possible_files = ['ERD.md', 'erd.md', 'diagrams/ERD.md', 'docs/ERD.md']
        for f in possible_files:
            if os.path.exists(f):
                with open(f, 'r') as file:
                    content = file.read()
                assert 'erDiagram' in content
                return
        pytest.fail("No ERD file found.")

    def test_erd_contains_all_entities(self):
        """ERD diagram contains all required entities."""
        import os
        possible_files = ['ERD.md', 'erd.md', 'diagrams/ERD.md', 'docs/ERD.md']
        for f in possible_files:
            if os.path.exists(f):
                with open(f, 'r') as file:
                    content = file.read()
                assert 'USER' in content.upper() or 'User' in content
                assert 'PLACE' in content.upper() or 'Place' in content
                assert 'REVIEW' in content.upper() or 'Review' in content
                assert 'AMENITY' in content.upper() or 'Amenity' in content
                return
        pytest.fail("No ERD file found.")
