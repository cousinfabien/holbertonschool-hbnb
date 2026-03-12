from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new review"""
        current_user = get_jwt_identity()
        data = request.json

        # Place exists check
        place = facade.get_place(data['place_id'])
        if not place:
            return {'error': 'Place not found'},404

        # Review own place prevention
        if place.owner_id == current_user:
            return{'error': 'You cannot review your own place'}, 400

        # Multiple reviews by the same user prevention
        existing_reviews = facade.get_reviews_by_user_and_place(current_user, place.id)
        if existing_reviews:
            return {'error': 'You have already reviewed this place'}, 400

        # Add user.id from JWT
        data['user_id'] = current_user

        try:
            r = facade.create_review(data)
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
        """Get review details by ID"""
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

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, review_id):
        """Update a review's information"""
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)

        if review is None:
            return {'error': 'Review not found'}, 404

        # Only author can update check
        if review.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            r = facade.update_review(review_id, request.json)
            if r is None:
                return {'error': 'Review not found'}, 404
            return {
                'id': r.id,
                'text': r.text,
                'rating': r.rating,
                'user_id': r.user_id,
                'place_id': r.place_id
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)

        if review is None:
            return {'error': 'Review not found'}, 404

        # Only user can delete check
        if review.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        success = facade.delete_review(review_id)
        if not success:
            return {'error': 'Review not found'}, 404
        return {'message': 'Review deleted successfully'}, 200
