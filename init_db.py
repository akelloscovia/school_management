"""
Database initialization script
Run this before seed_data.py
"""

import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

def init_db():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
