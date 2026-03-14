#!/usr/bin/python3
import re
from app.extensions import db, bcrypt
from app.models.base_model import BaseModel

class User(BaseModel):
    __tablename__ = 'users'  # Name of the table in the database

    # Columns mapped to the database
    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(120), nullable=False, unique=True)
    password   = db.Column(db.String(128), nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)
    
    def update_profile(self, data):
        """Update user profile with validation"""
        if "first_name" in data:
            if not data["first_name"] or len(data["first_name"]) > 50:
                raise ValueError("Invalid first_name")
        if "last_name" in data:
            if not data["last_name"] or len(data["last_name"]) > 50:
                raise ValueError("Invalid last_name")
        if "email" in data:
            if not data["email"] or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                raise ValueError("Invalid email")
        # All validations passed, now apply the changes and update the timestamp
        self.update(data)
