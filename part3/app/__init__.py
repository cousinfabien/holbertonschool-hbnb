#!/usr/bin/python3
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
# SQLAlchemy extension for database support
from flask_sqlalchemy import SQLAlchemy
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
import config as app_config

bcrypt = Bcrypt()
jwt = JWTManager()
# Create SQLAlchemy instance outside create_app() so models can import it
db = SQLAlchemy()

def create_app(config_class=app_config.DevelopmentConfig):
    """
    Application Factory for Flask.
    Returns a Flask app with all API namespaces registered.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    # Bind SQLAlchemy to the Flask app (reads SQLALCHEMY_DATABASE_URI from config)
    db.init_app(app)

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
    
    return app
    
