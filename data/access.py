import os.path
from dataclasses import dataclass
from datetime import datetime

import sqlite3

import bcrypt


@dataclass
class room_dto:
    room_id: int
    name: str
    capacity: int
    location: str
    available: bool  # True, wenn der Raum verfügbar ist, False, wenn nicht


@dataclass
class user_dto:
    user_id: int
    username: str
    email: str
    password: str  # Im echten Einsatz sollte das Passwort verschlüsselt und sicher gespeichert werden

@dataclass
class booking_dto:
    booking_id: int
    user_id: int
    room_id: int
    date: datetime
    start_time: datetime
    end_time: datetime
    purpose: str

def __init_database(cls):
    """
    Initializes the database incase tables are missing
    """
    class new_cls:
        def __init__(self, db_file: str, *args, **kwargs):
            self.db_instance = cls(db_file, *args, **kwargs)
            self.init_db(db_file)

        def __getattr__(self, item):
            return getattr(self.db_instance, item)

        def init_db(self, db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone() is None:
                cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            email TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        )
                    ''')
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rooms'")
            if cursor.fetchone() is None:
                cursor.execute('''
                        CREATE TABLE IF NOT EXISTS rooms (
                            room_id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            capacity INTEGER NOT NULL,
                            location TEXT NOT NULL,
                            available BOOLEAN NOT NULL
                        )
                    ''')
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookings'")
            if cursor.fetchone() is None:
                cursor.execute('''
                        CREATE TABLE IF NOT EXISTS bookings (
                            booking_id INTEGER PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            room_id INTEGER NOT NULL,
                            start_time TEXT NOT NULL,
                            end_time TEXT NOT NULL,
                            purpose TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users (user_id),
                            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
                        )
                    ''')

            conn.commit()
            conn.close()

    return new_cls


@__init_database
class room_dao:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row

    def add_room(self, room_dto):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO rooms (name, capacity, location, available)
                VALUES (?, ?, ?, ?)
            ''', (room_dto.name, room_dto.capacity, room_dto.location, room_dto.available))
            return cursor.lastrowid

    # Weitere Methoden für das Abrufen, Aktualisieren und Löschen von Räumen

    def get_room_by_id(self, room_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM rooms WHERE room_id = ?
            ''', (room_id,))
            return cursor.fetchone()

    def get_all_rooms(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM rooms
            ''')
            return cursor.fetchall()

    def update_room(self, room_dto):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE rooms SET name = ?, capacity = ?, location = ?, available = ? WHERE room_id = ?
            ''', (room_dto.name, room_dto.capacity, room_dto.location, room_dto.available, room_dto.room_id))
            return cursor.lastrowid

    def delete_room(self, room_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM rooms WHERE room_id = ?
            ''', (room_id,))
            return cursor.lastrowid

    def get_available_rooms(self, start_time, end_time):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM rooms WHERE available = ? AND room_id NOT IN (
                    SELECT room_id FROM bookings WHERE start_time <= ? AND end_time >= ?
                )
            ''', (True, end_time, start_time))
            return cursor.fetchall()

    def get_room_availability(self, room_id, date):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM rooms WHERE room_id = ? AND available = ? AND room_id NOT IN (
                    SELECT room_id FROM bookings WHERE start_time <= ? AND end_time >= ?
                )
            ''', (room_id, True, date, date))
            return cursor.fetchone()

    def get_room_bookings(self, room_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings WHERE room_id = ?
            ''', (room_id,))
            return cursor.fetchall()


@__init_database
class booking_dao:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row

    def add_booking(self, booking_dto):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (user_id, room_id, start_time, end_time, purpose)
                VALUES (?, ?, ?, ?, ?)
            ''', (booking_dto.user_id, booking_dto.room_id, booking_dto.start_time, booking_dto.end_time, booking_dto.purpose))
            return cursor.lastrowid

    def get_booking_by_id(self, booking_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings WHERE booking_id = ?
            ''', (booking_id,))
            return cursor.fetchone()

    def get_all_bookings(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings
            ''')
            return cursor.fetchall()

    def update_booking(self, booking_dto):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE bookings SET user_id = ?, room_id = ?, start_time = ?, end_time = ?, purpose = ? WHERE booking_id = ?
            ''', (booking_dto.user_id, booking_dto.room_id, booking_dto.start_time, booking_dto.end_time, booking_dto.purpose, booking_dto.booking_id))
            return cursor.lastrowid

    def delete_booking(self, booking_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM bookings WHERE booking_id = ?
            ''', (booking_id,))
            return cursor.lastrowid

    def get_bookings_by_user(self, user_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings WHERE user_id = ?
            ''', (user_id,))
            return cursor.fetchall()

    def get_bookings_by_room(self, room_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings WHERE room_id = ?
            ''', (room_id,))
            return cursor.fetchall()

    def get_bookings_by_date(self, date):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings WHERE start_time LIKE ?
            ''', (date.strftime('%Y-%m-%d') + '%',))
            return cursor.fetchall()

@__init_database
class user_dao:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)

    def add_user(self, user_dto):
        hashed_password = bcrypt.hashpw(user_dto.password.encode('utf-16'), bcrypt.gensalt())
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (user_dto.username, user_dto.email, hashed_password))
        self.conn.commit()

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return user_dto(row[0], row[1], row[2], row[3], False)
        return None


    def check_password(self, username, password):
        user = self.get_user_by_username(username)
        if user:
            return bcrypt.checkpw(password.encode('utf-16'), user.password)
        return False

    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return user_dto(row[0], row[1], row[2], row[3])
        return None

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append(user_dto(row[0], row[1], row[2], row[3]))
        return users

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def update_user(self, user_dto):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET username = ?, email = ?, password = ? WHERE user_id = ?",
                       (user_dto.username, user_dto.email, user_dto.password, user_dto.user_id))
        self.conn.commit()

    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return user_dto(row[0], row[1], row[2], row[3])
        return None
