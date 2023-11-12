import os

from flask import Flask, jsonify, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
from data.access import room_dao, booking_dao, user_dao  # Import your DAO classes
from data.access import room_dto, user_dto, booking_dto  # Import your DTO classes

db = "reservation.db"
app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# User endpoints
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    new_user = user_dto(None, data['username'], data['email'], data['password'])
    user_id = user_dao(db).add_user(new_user)
    return jsonify({'user_id': user_id}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    # Assume user_dto has a method to update its fields from a dictionary
    print(data)
    data['user_id'] = user_id
    data = user_dto(**data)
    user_dao(db).update_user(data)
    return jsonify({'success': True}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    user_dao(db).delete_user(user_id)
    return jsonify({'success': True}), 200

@app.route('/users', methods=['GET'])
def list_users():
    users = user_dao(db).get_all_users()

    return jsonify([user._asdict() for user in users])

# Room endpoints
@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.get_json()
    new_room = room_dto(**data)
    room_id = room_dao(db).add_room(new_room)
    return jsonify({'room_id': room_id}), 201

@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.get_json()
    room_to_update = room_dto(**data)
    room_dao(db).update_room(room_to_update)
    return jsonify({'success': True}), 200

@app.route('/rooms', methods=['GET'])
def get_rooms():
    all_rooms = room_dao(db).get_all_rooms()
    # Use list comprehension for eager fetching of room data
    return jsonify([dict(room) for room in all_rooms])

@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_single_room(room_id):
    room = room_dao(db).get_room_by_id(room_id)
    return jsonify(dict(room))

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room_dao(db).delete_room(room_id)
    return jsonify({'success': True}), 200


# Booking endpoints
@app.route('/bookings', methods=['POST'])
def make_booking():
    data = request.get_json()
    new_booking = booking_dto(**data)
    booking_id = booking_dao(db).add_booking(new_booking)
    return jsonify({'booking_id': booking_id}), 201

@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def remove_booking(booking_id):
    booking_dao(db).delete_booking(booking_id)
    return jsonify({'success': True}), 200

@app.route('/bookings/<int:booking_id>', methods=['PUT'])
def change_booking(booking_id):
    data = request.get_json()
    updated_booking = booking_dto(**data)
    booking_dao(db).update_booking(updated_booking)
    return jsonify({'success': True}), 200

@app.route('/bookings', methods=['GET'])
def list_bookings():
    all_bookings = booking_dao(db).get_all_bookings()
    # Use map to apply a transformation to each booking
    return jsonify(list(map(lambda b: b._asdict(), all_bookings)))

# Availability check
@app.route('/rooms/check', methods=['GET'])
def check_rooms():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    # Use filter to find rooms that are available between the given times
    available_rooms = filter(lambda room: room_dao(db).get_room_availability(room.room_id, start_time, end_time), room_dao(db).get_all_rooms())
    return jsonify([room._asdict() for room in available_rooms])

#delete all booking records when deleting a room i.e. cascade delete using functional programming features like lambda algorithm and filter and such
@app.route('/rooms/<int:room_id>/delete', methods=['DELETE'])
def delete_room_and_bookings(room_id):
    # Create instances of your DAOs
    room_data_access = room_dao(db)
    booking_data_access = booking_dao(db)

    # Retrieve all bookings for the specified room
    bookings_to_delete = booking_data_access.get_bookings_by_room(room_id)

    # Use a lambda function within a list comprehension to delete each booking
    [lambda booking: booking_data_access.delete_booking(booking['booking_id']) for booking in bookings_to_delete]

    # After deleting all bookings, delete the room
    room_data_access.delete_room(room_id)

    return jsonify({'success': True}), 200

@app.route('/db/delete', methods=['GET'])
def reset_db():
    try:
        os.remove(db)
    except FileNotFoundError:
        pass
    return jsonify({'success': True}), 200

if __name__ == '__main__':
    app.run(debug=True)
