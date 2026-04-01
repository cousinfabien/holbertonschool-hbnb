from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('places', description='Place operations')

# --------------------------------------
# Define the models for related entities
# --------------------------------------
# Adding the amenity model
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

# Adding the user model
user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Adding the review model
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

# Adding the place model for input validation and documentation 
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

# --------------------------------------
# 
# --------------------------------------
@api.route('/')
class PlaceList(Resource):
    # 
    @jwt_required()
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Missing or invalid token')
    def post(self):
        """Create a new place (authenticated users only)"""
        current_user = get_jwt_identity()
        place_data = request.json
        # Force owner_id to be the authenticated user
        place_data['owner_id'] = current_user
        try:
            place = facade.create_place(place_data)
            return {
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'owner_id': place.owner_id
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places (public)"""
        places = facade.get_all_places()
        return [{
            'id': p.id,
            'title': p.title,
            'latitude': p.latitude,
            'longitude': p.longitude,
            'price': p.price,
            'description': p.description
        } for p in places], 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID (public)"""
        place = facade.get_place(place_id)
        if place is None:
            return {'error': 'Place not found'}, 404
        reviews = facade.get_reviews_by_place(place_id)
        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': getattr(place.owner, 'id', None),
                'first_name': getattr(place.owner, 'first_name', None),
                'last_name': getattr(place.owner, 'last_name', None),
                'email': getattr(place.owner, 'email', None)
            } if getattr(place, 'owner', None) else None,
            'amenities': [{'id': a.id, 'name': a.name} for a in getattr(place, 'amenities', [])],
            'reviews': [{'id': r.id, 'text': r.text, 'rating': r.rating, 'user_id': r.user_id} for r in reviews] if reviews else []
        }, 200

    @jwt_required()
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place (owner or admin)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        current_user = get_jwt_identity()

        # Check place
        place = facade.get_place(place_id)
        if place is None:
            return {'error': 'Place not found'}, 404
        # Admin bypasses ownership check
        if not is_admin and place.owner_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            updated_place = facade.update_place(place_id, request.json)
            if updated_place is None:
                return {'error': 'Place not found'}, 404
            return {
                'id': updated_place.id,
                'title': updated_place.title,
                'description': updated_place.description,
                'price': updated_place.price,
                'latitude': updated_place.latitude,
                'longitude': updated_place.longitude,
                'owner_id': updated_place.owner_id
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400

# 
@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        reviews = facade.get_reviews_by_place(place_id)
        if reviews is None:
            return {'error': 'Place not found'}, 404
        return [{
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'user_id': r.user_id
            } for r in reviews], 200
