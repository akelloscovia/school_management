from app import db
from datetime import datetime


class Marks(db.Model):
    """Examination marks model"""
    __tablename__ = 'marks'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    term = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    exam_type = db.Column(db.String(50), nullable=False)  # midterm, final, etc.
    marks_obtained = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Float, nullable=False, default=100)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(2))  # A, B, C, D, E, F
    academic_year = db.Column(db.String(20), nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    recorded_by = db.relationship('User', backref='marks_recorded')
    
    def calculate_percentage(self):
        """Calculate percentage"""
        if self.total_marks > 0:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
    
    def assign_grade(self):
        """Assign grade based on percentage"""
        if not self.percentage:
            self.calculate_percentage()
        
        if self.percentage >= 90:
            self.grade = 'A'
        elif self.percentage >= 80:
            self.grade = 'B'
        elif self.percentage >= 70:
            self.grade = 'C'
        elif self.percentage >= 60:
            self.grade = 'D'
        elif self.percentage >= 50:
            self.grade = 'E'
        else:
            self.grade = 'F'
    
    def to_dict(self, include_subject=False, include_student=False):
        """Convert to dictionary"""
        self.calculate_percentage()
        self.assign_grade()
        
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'term': self.term,
            'exam_type': self.exam_type,
            'marks_obtained': self.marks_obtained,
            'total_marks': self.total_marks,
            'percentage': round(self.percentage, 2),
            'grade': self.grade,
            'academic_year': self.academic_year,
            'recorded_at': self.recorded_at.isoformat()
        }
        
        if include_subject:
            data['subject'] = self.subject.to_dict()
        if include_student:
            data['student'] = self.student.to_dict()
        
        return data


class TermReport(db.Model):
    """Term report card model"""
    __tablename__ = 'term_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    term = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    total_marks = db.Column(db.Float)
    average_percentage = db.Column(db.Float)
    class_rank = db.Column(db.Integer)
    teacher_remarks = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'term': self.term,
            'academic_year': self.academic_year,
            'total_marks': self.total_marks,
            'average_percentage': round(self.average_percentage, 2) if self.average_percentage else None,
            'class_rank': self.class_rank,
            'teacher_remarks': self.teacher_remarks,
            'generated_at': self.generated_at.isoformat()
        }
