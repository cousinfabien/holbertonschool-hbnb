#!/usr/bin/python3
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
# Import the shared facade instance to ensure a single in-memory data context.
# Avoids creating multiple HBnBFacade instances with isolated state.
from app.services import facade

# Create the "users" namespace
api = Namespace('users', description='User operations')

# User model for input validation and Swagger documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description="Password of the user")
})

# ------------------- User List / Create -------------------
@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input data or email already registered')
    def post(self):
        """Register a new user"""
        user_data = api.payload

        try:
            # Create a new user
            # The facade checks for duplicates and raises ValueError if found
            new_user = facade.create_user(user_data)
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email
            }, 201
        except ValueError as e:
            # We catch the error and return the 400 status code expected by Postman
            return {'error': str(e)}, 400

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve all users"""
        users = facade.get_all_users()
        users_list = [{
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        } for user in users]
        return users_list, 200

# ------------------- Retrieve / Update a single user -------------------
@api.route('/<string:user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Retrieve a single user by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }, 200

    @api.expect(user_model, validate=True)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid input data or email already registered')
    @api.response(404, 'User not found')
    @jwt_required()
    def put(self, user_id):
        """Update an existing user"""
        current_user = get_jwt_identity()
        if user_id != current_user:
            return {'error': 'Unauthorized action'}, 403
        user_data = api.payload

        # email or password modification prevention
        if 'email' in user_data or 'password' in user_data:
            return {'error': 'You cannot modify email or password'}, 400

        # Update the user
        try:
            updated_user = facade.update_user(user_id, user_data)
            # If the facade returns None, the user doesn't exist
            if not updated_user:
                return {'error': 'User not found'}, 404
        except ValueError as e:
            # The facade raises a ValueError if the email is taken
            return {'error': str(e)}, 400

        return {
            'id': updated_user.id,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'email': updated_user.email
        }, 200
