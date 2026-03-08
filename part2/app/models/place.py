#!/usr/bin/python3

from app.models.base_model import BaseModel


class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner_id):
        super().__init__()

        try:
            price = float(price)
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            raise ValueError("Price, latitude, and longitude must be valid numbers")

        if not title or len(title) > 100:
            raise ValueError("Invalid title")

        if price <= 0:
            raise ValueError("Price must be positive")

        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid latitude")

        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid longitude")

        if not isinstance(owner_id, str) or not owner_id.strip():
            raise ValueError("Invalid owner_id")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id

        self.reviews = [] # List to store related reviews
        self.amenities = [] # List to store related amenities


    def add_review(self, review):
        """
        Add a review to the place.
        """
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """
        Add an amenity to the place.
        """
        self.amenities.append(amenity)

    def update_details(self, data):
        """Update place details with validation"""
        if "title" in data:
            if not data["title"] or len(data["title"]) > 100:
                raise ValueError("Invalid title")

        if "price" in data:
            try:
                data["price"] = float(data["price"])
            except (ValueError, TypeError):
                raise ValueError("Price must be a valid number")
            if data["price"] <= 0:
                raise ValueError("Price must be positive")

        if "latitude" in data:
            try:
                data["latitude"] = float(data["latitude"])
            except (ValueError, TypeError):
                raise ValueError("Latitude must be a valid number")
            if not (-90 <= data["latitude"] <= 90):
                raise ValueError("Latitude must be between -90 and 90")

        if "longitude" in data:
            try:
                data["longitude"] = float(data["longitude"])
            except (ValueError, TypeError):
                raise ValueError("Longitude must be a valid number")
            if not (-180 <= data["longitude"] <= 180):
                raise ValueError("Longitude must be between -180 and 180")

        # All validations passed, now apply the changes and update the timestamp
        self.update(data)
