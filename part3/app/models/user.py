#!/usr/bin/python3
import re
from app.models.base_model import BaseModel

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password="", is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("Invalid first_name")

        if not last_name or len(last_name) > 50:
            raise ValueError("Invalid last_name")

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []

        # hashing password
        self.password = None
        if password:
            self.hash_password(password)
    
    def hash_password(self, password):
        """Hashes the password before storing"""
        from app import bcrypt
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Check if password matches with stored hash"""
        from app import bcrypt
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

    def to_dict(self):
        """Return dictionary representation
        without password (protection)"""
        data = super().to_dict()
        if "password" in data:
            del data["password"]
        return data
