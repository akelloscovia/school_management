"""
Database seeding script to populate initial data
Run this after setting up the database
"""

import os
from dotenv import load_dotenv
import secrets
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Role, Student, Class, Subject, Attendance, AttendanceStatus

# Load environment variables from .env
load_dotenv()

app = create_app(os.getenv('FLASK_ENV', 'development'))

def seed_database():
    with app.app_context():
        # Clear existing data (optional - comment out for production)
        # db.drop_all()
        # db.create_all()
        
        print("Seeding database...")
        
        # Create roles if they don't exist
        roles_data = [
            {'name': 'admin', 'description': 'Administrator'},
            {'name': 'teacher', 'description': 'Teacher'},
            {'name': 'student', 'description': 'Student'},
            {'name': 'parent', 'description': 'Parent'},
            {'name': 'accountant', 'description': 'Accountant'}
        ]
        
        for role_data in roles_data:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(**role_data)
                db.session.add(role)
                print(f"Created role: {role_data['name']}")
        
        db.session.commit()
        
        # Create admin user if it doesn't exist
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@school.com')
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not User.query.filter_by(email=admin_email).first():
            admin_role = Role.query.filter_by(name='admin').first()
            admin = User(
                first_name='Admin',
                last_name='User',
                email=admin_email,
                phone=os.getenv('ADMIN_PHONE', '1234567890'),
                role_id=admin_role.id
            )
            if not admin_password:
                admin_password = secrets.token_urlsafe(12)
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f"Created admin user: {admin_email}")
            print(f"Admin password: {admin_password}")
        
        # Create sample teacher
        teacher_email = os.getenv('TEACHER_EMAIL', 'teacher@school.com')
        teacher_password = os.getenv('TEACHER_PASSWORD')
        if not User.query.filter_by(email=teacher_email).first():
            teacher_role = Role.query.filter_by(name='teacher').first()
            teacher = User(
                first_name='John',
                last_name='Teacher',
                email=teacher_email,
                phone=os.getenv('TEACHER_PHONE', '9876543210'),
                role_id=teacher_role.id
            )
            if not teacher_password:
                teacher_password = secrets.token_urlsafe(12)
            teacher.set_password(teacher_password)
            db.session.add(teacher)
            print(f"Created teacher user: {teacher_email}")
            print(f"Teacher password: {teacher_password}")
        
        db.session.commit()
        
        # Create all classes matching frontend expectations
        classes_data = [
            {'name': 'Baby Class', 'level': 'Baby Class', 'academic_year': '2026', 'max_capacity': 30, 'description': 'Baby Class'},
            {'name': 'Middle Class', 'level': 'Middle Class', 'academic_year': '2026', 'max_capacity': 40, 'description': 'Middle Class'},
            {'name': 'Top Class', 'level': 'Top Class', 'academic_year': '2026', 'max_capacity': 45, 'description': 'Top Class'},
            {'name': 'P1', 'level': 'P1', 'academic_year': '2026', 'max_capacity': 48, 'description': 'Primary 1'},
            {'name': 'P2', 'level': 'P2', 'academic_year': '2026', 'max_capacity': 48, 'description': 'Primary 2'},
            {'name': 'P3', 'level': 'P3', 'academic_year': '2026', 'max_capacity': 48, 'description': 'Primary 3'},
            {'name': 'P4', 'level': 'P4', 'academic_year': '2026', 'max_capacity': 48, 'description': 'Primary 4'},
            {'name': 'P5', 'level': 'P5', 'academic_year': '2026', 'max_capacity': 50, 'description': 'Primary 5'},
            {'name': 'P6', 'level': 'P6', 'academic_year': '2026', 'max_capacity': 50, 'description': 'Primary 6'},
            {'name': 'P7', 'level': 'P7', 'academic_year': '2026', 'max_capacity': 50, 'description': 'Primary 7'},
        ]
        
        teacher = User.query.filter_by(email=teacher_email).first()
        created_class_id = None
        
        for class_data in classes_data:
            existing_class = Class.query.filter_by(name=class_data['name']).first()
            if not existing_class:
                class_obj = Class(
                    name=class_data['name'],
                    level=class_data['level'],
                    teacher_id=teacher.id if teacher else None,
                    academic_year=class_data['academic_year'],
                    max_capacity=class_data['max_capacity'],
                    description=class_data['description']
                )
                db.session.add(class_obj)
                print(f"Created class: {class_data['name']}")
                if created_class_id is None:
                    db.session.flush()
                    created_class_id = class_obj.id
        
        db.session.commit()
        
        # Create sample subjects
        if created_class_id:
            subjects_data = [
                {'name': 'Mathematics', 'code': 'MATH101'},
                {'name': 'English', 'code': 'ENG101'},
                {'name': 'Science', 'code': 'SCI101'},
                {'name': 'History', 'code': 'HIST101'}
            ]
            
            for subject_data in subjects_data:
                existing_subject = Subject.query.filter_by(code=subject_data['code']).first()
                if not existing_subject:
                    subject = Subject(
                        name=subject_data['name'],
                        code=subject_data['code'],
                        class_id=created_class_id,
                        credit_hours=40
                    )
                    db.session.add(subject)
                    print(f"Created subject: {subject_data['name']}")
        
        db.session.commit()
        
        # Create sample students
        student_role = Role.query.filter_by(name='student').first()
        for i in range(5):
            student_email = f'student{i+1}@school.com'
            if not User.query.filter_by(email=student_email).first():
                user = User(
                    first_name=f'Student{i+1}',
                    last_name='Pupil',
                    email=student_email,
                    phone=f'555000{i}',
                    role_id=student_role.id
                )
                student_password = os.getenv(f'STUDENT_PASSWORD_{i+1}') or os.getenv('STUDENT_PASSWORD')
                if not student_password:
                    student_password = secrets.token_urlsafe(10)
                user.set_password(student_password)
                db.session.add(user)
                db.session.flush()
                
                # Create student profile
                student = Student(
                    user_id=user.id,
                    admission_number=f'ADM2023{i+1:04d}',
                    date_of_birth=(datetime.now() - timedelta(days=365*15)).date(),
                    gender='Male' if i % 2 == 0 else 'Female',
                    address=f'{i+1} School Street',
                    class_id=created_class_id if created_class_id else None
                )
                db.session.add(student)
                print(f"Created student: {student_email}")
                print(f"Student password: {student_password}")
        
        db.session.commit()
        
        # Create sample attendance records
        students = Student.query.all()
        for student in students[:2]:  # Add attendance for first 2 students
            for i in range(20):
                attendance_date = datetime.now().date() - timedelta(days=20-i)
                existing_attendance = Attendance.query.filter_by(
                    student_id=student.id,
                    date=attendance_date
                ).first()
                
                if not existing_attendance:
                    status = AttendanceStatus.PRESENT if i % 5 != 0 else AttendanceStatus.ABSENT
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        recorded_by_id=1
                    )
                    db.session.add(attendance)
            
            print(f"Created attendance records for student: {student.user.email}")
        
        db.session.commit()
        
        print("Database seeding completed!")

if __name__ == '__main__':
    seed_database()
