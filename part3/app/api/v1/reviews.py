from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade
from flask import request

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @jwt_required()
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Missing or invalid token')
    def post(self):
        """Create a new review (authenticated users only)"""
        current_user = get_jwt_identity()
        review_data = request.json
        # Force user_id to be the authenticated user
        review_data['user_id'] = current_user

        # Check that the place exists
        place = facade.get_place(review_data['place_id'])
        if place is None:
            return {'error': 'Place not found'}, 404

        # Check that the user is not reviewing their own place
        if place.owner_id == current_user:
            return {'error': 'You cannot review your own place'}, 400

        # Check that the user has not already reviewed this place
        existing_reviews = facade.get_reviews_by_place(review_data['place_id'])
        for review in existing_reviews:
            if review.user_id == current_user:
                return {'error': 'You have already reviewed this place'}, 400
        try:
            r = facade.create_review(review_data)
            return {
                'id': r.id,
                'text': r.text,
                'rating': r.rating,
                'user_id': r.user_id,
                'place_id': r.place_id
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        return [{
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'user_id': r.user_id,
            'place_id': r.place_id
        } for r in reviews], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID (public)"""
        r = facade.get_review(review_id)
        if r is None:
            return {'error': 'Review not found'}, 404
        return {
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'user_id': r.user_id,
            'place_id': r.place_id
        }, 200

    @jwt_required()
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review (author only)"""
        current_user = get_jwt_identity()

        # Check that the review exists
        r = facade.get_review(review_id)
        if r is None:
            return {'error': 'Review not found'}, 404

        # Check ownership
        if r.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            updated = facade.update_review(review_id, request.json)
            return {
                'id': updated.id,
                'text': updated.text,
                'rating': updated.rating,
                'user_id': updated.user_id,
                'place_id': updated.place_id
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @jwt_required()
    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review (author only)"""
        current_user = get_jwt_identity()
        
        success = facade.get_review(review_id)
        if success is None:
            return {'error': 'Review not found'}, 404
        # Check ownership
        if success.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403
        
        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200
