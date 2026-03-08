#!/usr/bin/python3
"""
HBNB Part 2 - Full API Test Suite
Tests all API endpoints: 20X success responses, 40X error responses, and edge cases.
Uses Flask's built-in test client — no need to run the server manually.

Run with:
    python -m pytest app/tests/test_models.py -v
or:
    python app/tests/test_models.py
"""

import sys
import os
import json
import unittest

# Ensure Python can find the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app


class TestBase(unittest.TestCase):
    """Base test class — sets up the Flask test client and shared state."""

    # Shared IDs across tests (populated as tests run in order)
    user_id = None
    user_id_2 = None
    amenity_id = None
    amenity_id_2 = None
    place_id = None
    review_id = None

    @classmethod
    def setUpClass(cls):
        """Create the Flask app and test client once for all tests."""
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def post(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

    def get(self, url):
        return self.client.get(url)

    def put(self, url, data):
        return self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

    def delete(self, url):
        return self.client.delete(url)

    def json(self, response):
        return json.loads(response.data)


# =============================================================================
# USERS
# =============================================================================

class TestUsers(TestBase):
    """Test suite for /api/v1/users/ endpoints."""

    def test_01_create_user_201(self):
        """POST /users/ - Create first user successfully (201)."""
        res = self.post('/api/v1/users/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        })
        self.assertEqual(res.status_code, 201)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertEqual(data['email'], 'john.doe@example.com')
        TestBase.user_id = data['id']

    def test_02_create_second_user_201(self):
        """POST /users/ - Create second user successfully (201)."""
        res = self.post('/api/v1/users/', {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com'
        })
        self.assertEqual(res.status_code, 201)
        data = self.json(res)
        self.assertIn('id', data)
        TestBase.user_id_2 = data['id']

    def test_03_create_user_duplicate_email_400(self):
        """POST /users/ - Duplicate email should return 400."""
        res = self.post('/api/v1/users/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        })
        self.assertEqual(res.status_code, 400)
        data = self.json(res)
        self.assertIn('error', data)
        self.assertIn('Email already registered', data['error'])

    def test_04_create_user_invalid_email_400(self):
        """POST /users/ - Invalid email format should return 400."""
        res = self.post('/api/v1/users/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'not-a-valid-email'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', self.json(res))

    def test_05_create_user_missing_field_400(self):
        """POST /users/ - Missing required field should return 400."""
        res = self.post('/api/v1/users/', {
            'first_name': 'John'
        })
        self.assertEqual(res.status_code, 400)

    def test_06_create_user_first_name_too_long_400(self):
        """POST /users/ - first_name exceeding 50 chars should return 400."""
        res = self.post('/api/v1/users/', {
            'first_name': 'A' * 51,
            'last_name': 'Doe',
            'email': 'toolong@example.com'
        })
        self.assertEqual(res.status_code, 400)

    def test_07_get_all_users_200(self):
        """GET /users/ - List all users should return 200 with array."""
        res = self.get('/api/v1/users/')
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    def test_08_get_user_by_id_200(self):
        """GET /users/:id - Get existing user should return 200."""
        res = self.get(f'/api/v1/users/{TestBase.user_id}')
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertEqual(data['id'], TestBase.user_id)
        self.assertIn('email', data)

    def test_09_get_user_not_found_404(self):
        """GET /users/:id - Nonexistent user should return 404."""
        res = self.get('/api/v1/users/nonexistent-id-0000')
        self.assertEqual(res.status_code, 404)
        self.assertIn('error', self.json(res))

    def test_10_update_user_200(self):
        """PUT /users/:id - Update user should return 200."""
        res = self.put(f'/api/v1/users/{TestBase.user_id}', {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.json(res)['first_name'], 'Johnny')

    def test_11_update_user_email_taken_400(self):
        """PUT /users/:id - Email already used by another user should return 400."""
        res = self.put(f'/api/v1/users/{TestBase.user_id}', {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'email': 'jane.smith@example.com'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Email already registered', self.json(res)['error'])

    def test_11b_update_user_invalid_email_400(self):
        """PUT /users/:id - Invalid email format should return 400."""
        res = self.put(f'/api/v1/users/{TestBase.user_id}', {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'email': 'not-a-valid-email'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', self.json(res))
    
    def test_12_update_user_not_found_404(self):
        """PUT /users/:id - Update nonexistent user should return 404."""
        res = self.put('/api/v1/users/nonexistent-id-0000', {
            'first_name': 'Ghost',
            'last_name': 'User',
            'email': 'ghost@example.com'
        })
        self.assertEqual(res.status_code, 404)


# =============================================================================
# AMENITIES
# =============================================================================

class TestAmenities(TestBase):
    """Test suite for /api/v1/amenities/ endpoints."""

    def test_01_create_amenity_201(self):
        """POST /amenities/ - Create first amenity successfully (201)."""
        res = self.post('/api/v1/amenities/', {'name': 'WiFi'})
        self.assertEqual(res.status_code, 201)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'WiFi')
        TestBase.amenity_id = data['id']

    def test_02_create_second_amenity_201(self):
        """POST /amenities/ - Create second amenity successfully (201)."""
        res = self.post('/api/v1/amenities/', {'name': 'Pool'})
        self.assertEqual(res.status_code, 201)
        data = self.json(res)
        self.assertIn('id', data)
        TestBase.amenity_id_2 = data['id']

    def test_03_create_amenity_duplicate_name_400(self):
        """POST /amenities/ - Duplicate name should return 400."""
        res = self.post('/api/v1/amenities/', {'name': 'WiFi'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', self.json(res))

    def test_04_create_amenity_empty_name_400(self):
        """POST /amenities/ - Empty name should return 400."""
        res = self.post('/api/v1/amenities/', {'name': ''})
        self.assertEqual(res.status_code, 400)

    def test_05_create_amenity_name_too_long_400(self):
        """POST /amenities/ - Name exceeding 50 chars should return 400."""
        res = self.post('/api/v1/amenities/', {'name': 'A' * 51})
        self.assertEqual(res.status_code, 400)

    def test_06_get_all_amenities_200(self):
        """GET /amenities/ - List all amenities should return 200 with array."""
        res = self.get('/api/v1/amenities/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(self.json(res), list)

    def test_07_get_amenity_by_id_200(self):
        """GET /amenities/:id - Get existing amenity should return 200."""
        res = self.get(f'/api/v1/amenities/{TestBase.amenity_id}')
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertIn('name', data)

    def test_08_get_amenity_not_found_404(self):
        """GET /amenities/:id - Nonexistent amenity should return 404."""
        res = self.get('/api/v1/amenities/nonexistent-id-0000')
        self.assertEqual(res.status_code, 404)
        self.assertIn('error', self.json(res))

    def test_09_update_amenity_200(self):
        """PUT /amenities/:id - Update amenity should return 200."""
        res = self.put(f'/api/v1/amenities/{TestBase.amenity_id}', {
            'name': 'High-Speed WiFi'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('amenity', self.json(res))

    def test_10_update_amenity_not_found_404(self):
        """PUT /amenities/:id - Update nonexistent amenity should return 404."""
        res = self.put('/api/v1/amenities/nonexistent-id-0000', {
            'name': 'Jacuzzi'
        })
        self.assertEqual(res.status_code, 404)

    def test_11_update_amenity_duplicate_name_400(self):
        """PUT /amenities/:id - Updating to a name already taken should return 400."""
        res = self.put(f'/api/v1/amenities/{TestBase.amenity_id}', {
            'name': 'Pool'
        })
        self.assertEqual(res.status_code, 400)

    def test_12_update_amenity_empty_name_400(self):
        """PUT /amenities/:id - Empty name should return 400."""
        res = self.put(f'/api/v1/amenities/{TestBase.amenity_id}', {
            'name': ''
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', self.json(res))

# =============================================================================
# PLACES
# =============================================================================

class TestPlaces(TestBase):
    """Test suite for /api/v1/places/ endpoints."""

    def test_01_create_place_201(self):
        """POST /places/ - Create place successfully (201)."""
        res = self.post('/api/v1/places/', {
            'title': 'Cozy Apartment',
            'description': 'A nice place to stay',
            'price': 120.0,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'owner_id': TestBase.user_id
        })
        self.assertEqual(res.status_code, 201)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertEqual(data['title'], 'Cozy Apartment')
        TestBase.place_id = data['id']

    def test_02_create_place_with_amenities_201(self):
        """POST /places/ - Create place with amenities should return 201."""
        res = self.post('/api/v1/places/', {
            'title': 'Beach House',
            'description': 'By the sea',
            'price': 250.0,
            'latitude': 43.2965,
            'longitude': 5.3698,
            'owner_id': TestBase.user_id,
            'amenities': [TestBase.amenity_id_2]
        })
        self.assertEqual(res.status_code, 201)

    def test_03_create_place_owner_not_found_400(self):
        """POST /places/ - Nonexistent owner_id should return 400."""
        res = self.post('/api/v1/places/', {
            'title': 'Ghost Place',
            'price': 100.0,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'owner_id': 'nonexistent-owner-id'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Owner not found', self.json(res)['error'])

    def test_04_create_place_negative_price_400(self):
        """POST /places/ - Negative price should return 400."""
        res = self.post('/api/v1/places/', {
            'title': 'Negative Price Place',
            'price': -50.0,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'owner_id': TestBase.user_id
        })
        self.assertEqual(res.status_code, 400)

    def test_05_create_place_invalid_latitude_400(self):
        """POST /places/ - Latitude out of range should return 400."""
        res = self.post('/api/v1/places/', {
            'title': 'Invalid Lat Place',
            'price': 100.0,
            'latitude': 999.0,
            'longitude': 2.3522,
            'owner_id': TestBase.user_id
        })
        self.assertEqual(res.status_code, 400)

    def test_06_create_place_invalid_longitude_400(self):
        """POST /places/ - Longitude out of range should return 400."""
        res = self.post('/api/v1/places/', {
            'title': 'Invalid Lon Place',
            'price': 100.0,
            'latitude': 48.8566,
            'longitude': 999.0,
            'owner_id': TestBase.user_id
        })
        self.assertEqual(res.status_code, 400)

    def test_07_create_place_amenity_not_found_400(self):
        """POST /places/ - Nonexistent amenity ID should return 400."""
        res = self.post('/api/v1/places/', {
            'title': 'Phantom Amenities',
            'price': 100.0,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'owner_id': TestBase.user_id,
            'amenities': ['nonexistent-amenity-id']
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Amenity not found', self.json(res)['error'])

    def test_08_create_place_missing_fields_400(self):
        """POST /places/ - Missing required fields should return 400."""
        res = self.post('/api/v1/places/', {
            'description': 'No title, no price, no coords'
        })
        self.assertEqual(res.status_code, 400)

    def test_09_get_all_places_200(self):
        """GET /places/ - List all places should return 200 with array."""
        res = self.get('/api/v1/places/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(self.json(res), list)

    def test_10_get_place_by_id_200(self):
        """GET /places/:id - Get existing place should return 200 with full details."""
        res = self.get(f'/api/v1/places/{TestBase.place_id}')
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertIn('owner', data)
        self.assertIsInstance(data['amenities'], list)
        self.assertIsInstance(data['reviews'], list)

    def test_11_get_place_not_found_404(self):
        """GET /places/:id - Nonexistent place should return 404."""
        res = self.get('/api/v1/places/nonexistent-id-0000')
        self.assertEqual(res.status_code, 404)
        self.assertIn('error', self.json(res))

    def test_12_update_place_200(self):
        """PUT /places/:id - Update place should return 200."""
        res = self.put(f'/api/v1/places/{TestBase.place_id}', {
            'title': 'Updated Apartment',
            'description': 'Even nicer now',
            'price': 150.0,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'owner_id': TestBase.user_id
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.json(res)['title'], 'Updated Apartment')

    def test_13_update_place_not_found_404(self):
        """PUT /places/:id - Update nonexistent place should return 404."""
        res = self.put('/api/v1/places/nonexistent-id-0000', {
            'title': 'Ghost Place',
            'price': 100.0,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'owner_id': TestBase.user_id
        })
        self.assertEqual(res.status_code, 404)

    def test_14_update_place_negative_price_400(self):
        """PUT /places/:id - Negative price in update should return 400."""
        res = self.put(f'/api/v1/places/{TestBase.place_id}', {
            'price': -99.0
        })
        self.assertEqual(res.status_code, 400)

    def test_14b_update_place_invalid_latitude_400(self):
        """PUT /places/:id - Latitude out of range should return 400."""
        res = self.put(f'/api/v1/places/{TestBase.place_id}', {
            'latitude': 999.0
        })
        self.assertEqual(res.status_code, 400)

    def test_14c_update_place_invalid_longitude_400(self):
        """PUT /places/:id - Longitude out of range should return 400."""
        res = self.put(f'/api/v1/places/{TestBase.place_id}', {
            'longitude': 999.0
        })
        self.assertEqual(res.status_code, 400)

    def test_15_get_reviews_by_place_200(self):
        """GET /places/:id/reviews - Get reviews for a place should return 200."""
        res = self.get(f'/api/v1/places/{TestBase.place_id}/reviews')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(self.json(res), list)

    def test_16_get_reviews_by_place_not_found_404(self):
        """GET /places/:id/reviews - Nonexistent place should return 404."""
        res = self.get('/api/v1/places/nonexistent-id-0000/reviews')
        self.assertEqual(res.status_code, 404)


# =============================================================================
# REVIEWS
# =============================================================================

class TestReviews(TestBase):
    """Test suite for /api/v1/reviews/ endpoints."""

    def test_01_create_review_201(self):
        """POST /reviews/ - Create review successfully (201)."""
        res = self.post('/api/v1/reviews/', {
            'text': 'Great place, loved it!',
            'rating': 4,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 201)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertEqual(data['rating'], 4)
        TestBase.review_id = data['id']

    def test_02_create_review_rating_zero_400(self):
        """POST /reviews/ - Rating of 0 should return 400."""
        res = self.post('/api/v1/reviews/', {
            'text': 'Too low rating',
            'rating': 0,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', self.json(res))

    def test_03_create_review_rating_above_5_400(self):
        """POST /reviews/ - Rating above 5 should return 400."""
        res = self.post('/api/v1/reviews/', {
            'text': 'Rating too high',
            'rating': 6,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 400)

    def test_04_create_review_missing_text_400(self):
        """POST /reviews/ - Missing text field should return 400."""
        res = self.post('/api/v1/reviews/', {
            'rating': 3,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 400)

    def test_05_create_review_user_not_found_400(self):
        """POST /reviews/ - Nonexistent user_id should return 400."""
        res = self.post('/api/v1/reviews/', {
            'text': 'Review from ghost user',
            'rating': 3,
            'user_id': 'nonexistent-user-id',
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('User not found', self.json(res)['error'])

    def test_06_create_review_place_not_found_400(self):
        """POST /reviews/ - Nonexistent place_id should return 400."""
        res = self.post('/api/v1/reviews/', {
            'text': 'Review for ghost place',
            'rating': 3,
            'user_id': TestBase.user_id_2,
            'place_id': 'nonexistent-place-id'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Place not found', self.json(res)['error'])

    def test_07_get_all_reviews_200(self):
        """GET /reviews/ - List all reviews should return 200 with array."""
        res = self.get('/api/v1/reviews/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(self.json(res), list)

    def test_08_get_review_by_id_200(self):
        """GET /reviews/:id - Get existing review should return 200."""
        res = self.get(f'/api/v1/reviews/{TestBase.review_id}')
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIn('id', data)
        self.assertIn('rating', data)
        self.assertIn('user_id', data)
        self.assertIn('place_id', data)

    def test_09_get_review_not_found_404(self):
        """GET /reviews/:id - Nonexistent review should return 404."""
        res = self.get('/api/v1/reviews/nonexistent-id-0000')
        self.assertEqual(res.status_code, 404)
        self.assertIn('error', self.json(res))

    def test_10_update_review_200(self):
        """PUT /reviews/:id - Update review should return 200."""
        res = self.put(f'/api/v1/reviews/{TestBase.review_id}', {
            'text': 'Updated review - even better!',
            'rating': 5,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.json(res)['rating'], 5)

    def test_11_update_review_invalid_rating_400(self):
        """PUT /reviews/:id - Rating of 10 should return 400."""
        res = self.put(f'/api/v1/reviews/{TestBase.review_id}', {
            'text': 'Bad rating',
            'rating': 10,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 400)

    def test_11b_update_review_empty_text_400(self):
        """PUT /reviews/:id - Empty text should return 400."""
        res = self.put(f'/api/v1/reviews/{TestBase.review_id}', {
            'text': '',
            'rating': 5,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', self.json(res))

    def test_12_update_review_not_found_404(self):
        """PUT /reviews/:id - Update nonexistent review should return 404."""
        res = self.put('/api/v1/reviews/nonexistent-id-0000', {
            'text': 'Does not matter',
            'rating': 3,
            'user_id': TestBase.user_id_2,
            'place_id': TestBase.place_id
        })
        self.assertEqual(res.status_code, 404)

    def test_13_delete_review_200(self):
        """DELETE /reviews/:id - Delete existing review should return 200."""
        res = self.delete(f'/api/v1/reviews/{TestBase.review_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn('message', self.json(res))

    def test_14_delete_review_already_deleted_404(self):
        """DELETE /reviews/:id - Delete already deleted review should return 404."""
        res = self.delete(f'/api/v1/reviews/{TestBase.review_id}')
        self.assertEqual(res.status_code, 404)
        self.assertIn('error', self.json(res))

    def test_15_delete_review_not_found_404(self):
        """DELETE /reviews/:id - Delete nonexistent review should return 404."""
        res = self.delete('/api/v1/reviews/nonexistent-id-0000')
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
