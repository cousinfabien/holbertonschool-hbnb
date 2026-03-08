#!/usr/bin/python3
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    def __init__(self, name, description=""):
        super().__init__()

        if not name or len(name) > 50:
            raise ValueError("Amenity name is required and cannot exceed 50 characters")

        self.name = name
        self.description = description
    
    def update_amenity(self, data):
        """Update amenity with validation"""
        if "name" in data:
            # .strip() checks if the name is empty or has only spaces
            if not data["name"] or not data["name"].strip():
                raise ValueError("Amenity name cannot be empty")
            if len(data["name"]) > 50:
                raise ValueError("Amenity name cannot exceed 50 characters")

        # All validations passed, now apply the changes and update the timestamp
        self.update(data)
