from app import db
from datetime import datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    """Attendance status options"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Attendance(db.Model):
    """Attendance tracking model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    remarks = db.Column(db.Text)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recorded_by = db.relationship('User', backref='attendance_records')
    
    # Composite unique constraint: a student can only have one attendance record per day
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='unique_student_date'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat(),
            'status': self.status.value,
            'remarks': self.remarks,
            'recorded_at': self.recorded_at.isoformat()
        }


class AttendanceSummary(db.Model):
    """Monthly attendance summary"""
    __tablename__ = 'attendance_summary'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_days = db.Column(db.Integer, default=0)
    present_days = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)
    late_days = db.Column(db.Integer, default=0)
    excused_days = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'year': self.year,
            'month': self.month,
            'total_days': self.total_days,
            'present_days': self.present_days,
            'absent_days': self.absent_days,
            'late_days': self.late_days,
            'excused_days': self.excused_days
        }
