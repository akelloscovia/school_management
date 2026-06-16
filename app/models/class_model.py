from app import db
from datetime import datetime


class Class(db.Model):
    """Class/Grade model"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    level = db.Column(db.String(50), nullable=False)  # e.g., Primary 1, Form 4
    stream = db.Column(db.String(50))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    academic_year = db.Column(db.String(20), nullable=False)
    max_capacity = db.Column(db.Integer, default=50)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subjects = db.relationship('Subject', backref='class_', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_teacher=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'stream': self.stream,
            'academic_year': self.academic_year,
            'max_capacity': self.max_capacity,
            'description': self.description,
            'student_count': len(self.students),
            'created_at': self.created_at.isoformat()
        }
        if include_teacher and self.teacher:
            data['teacher'] = self.teacher.to_dict()
        return data


class Subject(db.Model):
    """Subject model"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    description = db.Column(db.Text)
    credit_hours = db.Column(db.Integer, default=40)
    
    marks = db.relationship('Marks', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'class_id': self.class_id,
            'description': self.description,
            'credit_hours': self.credit_hours
        }
