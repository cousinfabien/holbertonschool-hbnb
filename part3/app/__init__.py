#!/usr/bin/python3
import os
from flask import Flask
from flask_restx import Api
from app.extensions import db, bcrypt, jwt

from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns

import config as app_config


def create_app(config_class=app_config.DevelopmentConfig):
    """
    Application Factory for Flask.
    Returns a Flask app with all API namespaces registered.
    """
    app = Flask(__name__)
    # Charge the configuration
    app.config.from_object(config_class)
    
    # Create instance/ folder if it doesn't exist
    os.makedirs(app.instance_path, exist_ok=True)
    # Build absolute path for SQLite database file
    db_path = os.path.join(app.instance_path, 'development.db')
    # Override URI with absolute path for reliability
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Initialice the extensions
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app) # NEW: Bind SQLAlchemy to the Flask app

    authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT token. Format: Bearer <token>'
        }
    }
    # Create the Flask-RestX API
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/',
        authorizations=authorizations,
        security='Bearer'
    )

    # Register the endpoins
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    
    # Create the tables if they don't exist
    #with app.app_context():
    #    db.create_all()
        # Permissions for DB file (read/write for everyone)

    return app
    
