"""
Reset database schema and recreate with new User model fields
"""
import os
from dotenv import load_dotenv
from app import create_app, db

load_dotenv()

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating new tables...")
    db.create_all()
    print("Database schema reset complete!")
