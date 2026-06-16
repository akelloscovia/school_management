"""
Conftest for pytest configuration
"""

import os
import pytest
from app import create_app, db
from app.models import User, Role, Student, Class

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database with sample data."""
    with app.app_context():
        # Create roles
        admin_role = Role(name='admin', description='Administrator')
        teacher_role = Role(name='teacher', description='Teacher')
        student_role = Role(name='student', description='Student')
        
        db.session.add_all([admin_role, teacher_role, student_role])
        db.session.commit()
        
        # Create admin user
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            role_id=admin_role.id
        )
        admin.set_password('admin123')
        
        # Create teacher
        teacher = User(
            first_name='John',
            last_name='Teacher',
            email='teacher@test.com',
            role_id=teacher_role.id
        )
        teacher.set_password('teacher123')
        
        db.session.add_all([admin, teacher])
        db.session.commit()
        
        # Create class
        class_obj = Class(
            name='Form 1A',
            level='Form 1',
            teacher_id=teacher.id,
            academic_year='2023/2024'
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        return {
            'admin': admin,
            'teacher': teacher,
            'student_role': student_role,
            'class': class_obj
        }
