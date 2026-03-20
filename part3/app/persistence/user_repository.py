#!/usr/bin/python3
from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        # Passes the User model to the parent class SQLAlchemyRepository
        super().__init__(User)

    def get_user_by_email(self, email):
        # SELECT * FROM users WHERE email = 'email' LIMIT 1
        return self.model.query.filter_by(email=email).first()
