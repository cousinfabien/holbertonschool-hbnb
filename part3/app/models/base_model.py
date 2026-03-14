#!/usr/bin/python3

import uuid
from datetime import datetime, timezone
from app.extensions import db


class BaseModel(db.Model):
    __abstract__ = True  # SQLAlchemy does not create a table for BaseModel

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now(timezone.utc)

    def update(self, data):
        """Update the attributes of the object based on the provided dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def delete(self):
        """Placeholder for delete operation"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
