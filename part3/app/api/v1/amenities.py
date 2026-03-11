#!/usr/bin/python3
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

# Modèle pour validation et Swagger
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})


# ------------------- Liste / Création -------------------
@api.route('/')
class AmenityList(Resource):
    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create a new amenity (admin only)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        try:
            amenity = facade.create_amenity(api.payload)
        except ValueError as e:
            return {'error': str(e)}, 400
        return {'id': amenity.id, 'name': amenity.name}, 201

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Lister toutes les amenities"""
        amenities = facade.get_all_amenities()
        return [{'id': a.id, 'name': a.name} for a in amenities], 200


# ------------------- Détail / Mise à jour -------------------
@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Récupérer une amenity par ID (public)"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {'id': amenity.id, 'name': amenity.name}, 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update an amenity (admin only)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        try:
            updated = facade.update_amenity(amenity_id, api.payload)
        except ValueError as e:
            return {'error': str(e)}, 400
        if not updated:
            return {'error': 'Amenity not found'}, 404
        return {
            'message': 'Amenity updated successfully',
            'amenity': {
                'id': updated.id,
                'name': updated.name
            }
        }, 200
