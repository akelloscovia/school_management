from app import db
from datetime import datetime


class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    admission_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text)
    medical_info = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    admission_status = db.Column(db.String(50), default='pending')
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    class_ = db.relationship('Class', backref='students')
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    marks = db.relationship('Marks', backref='student', lazy=True, cascade='all, delete-orphan')
    parents = db.relationship('StudentParent', backref='student', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('StudentDocument', backref='student', lazy=True, cascade='all, delete-orphan')
    transfers = db.relationship('StudentTransfer', backref='student', lazy=True, cascade='all, delete-orphan')
    promotions = db.relationship('PromotionHistory', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_user=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            'admission_number': self.admission_number,
            'date_of_birth': self.date_of_birth.isoformat(),
            'gender': self.gender,
            'parent_contact': self.parents[0].phone if self.parents else None,
            'class_name': self.class_.name if self.class_ else None,
            'address': self.address,
            'class_id': self.class_id,
            'enrollment_date': self.enrollment_date.isoformat(),
            'is_active': self.is_active
        }
        if include_user:
            data['user'] = self.user.to_dict()
        return data


class StudentParent(db.Model):
    """Student-Parent relationship model"""
    __tablename__ = 'student_parents'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_name = db.Column(db.String(150), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # Father, Mother, Guardian, etc.
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    occupation = db.Column(db.String(100))
    address = db.Column(db.Text)
    is_primary_contact = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='student_parent_records', foreign_keys=[user_id])

    def to_dict(self):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'parent_name': self.parent_name,
            'relationship': self.relationship,
            'phone': self.phone,
            'email': self.email,
            'occupation': self.occupation,
            'address': self.address,
            'is_primary_contact': self.is_primary_contact
        }
        if self.user:
            data['user'] = self.user.to_dict()
        return data
