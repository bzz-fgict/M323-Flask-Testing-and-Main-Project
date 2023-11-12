# test_app.py
import os
import unittest
import json
from main import app
from data.access import room_dao, user_dao, booking_dao  # Import your DAO classes

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # You can call your seeding function here if needed, or preferably
        # seed your test database manually before running tests

    def test_room_listing(self):
        # Test retrieving list of rooms
        response = self.app.get('/rooms')
        self.assertEqual(response.status_code, 200)

    def test_create_user(self):
        # Test user creation
        user_payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        }
        response = self.app.post('/users', json=user_payload)
        self.assertEqual(response.status_code, 201)

    # ... Add more test methods for each endpoint ...

    def test_create_room(self):
        # Test room creation
        room_payload = {
            "room_id": None,
            "name":"someroom",
            "capacity": 5,
            "location":"somewhere",
            "available": True
        }
        response = self.app.post('/rooms', json=room_payload)
        self.assertEqual(response.status_code, 201)


    def test_update_user(self):
        # Test user update
        user_payload = {
            'user_id': None,
            'username': 'newuser',
            'email': 'SOMETHING@gmail.com',
            'password': 'newpassword'
        }
        response = self.app.put('/users/1', json=user_payload)
        self.assertEqual(response.status_code, 200)

    def test_update_room(self):
        # Test room update
        room_payload = {
            "room_id": 1,
            "name":"someroom2",
            "capacity": 54,
            "location":"nowhere",
            "available": False
        }
        response = self.app.put('/rooms/1', json=room_payload)
        self.assertEqual(response.status_code, 200)



    def test_delete_user(self):
        # Test user deletion
        response = self.app.delete('/users/1')
        self.assertEqual(response.status_code, 200)

    def test_delete_room(self):
        # Test room deletion
        response = self.app.delete('/rooms/1')
        self.assertEqual(response.status_code, 200)

    def test_delete_booking(self):
        # Test booking deletion
        response = self.app.delete('/bookings/1')
        self.assertEqual(response.status_code, 200)



    def tearDown(self):
        # delete the file "reservation.db" if it exists
        os.remove("reservation.db");
        pass

if __name__ == '__main__':
    unittest.main()
