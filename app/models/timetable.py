from app import db
from datetime import datetime


class TimetableEntry(db.Model):
    """Timetable entry for a class"""
    __tablename__ = 'timetable_entries'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    venue = db.Column(db.String(100))
    academic_year = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'venue': self.venue,
            'academic_year': self.academic_year,
            'created_at': self.created_at.isoformat()
        }


class ClassNote(db.Model):
    """Notes or resources uploaded for a class"""
    __tablename__ = 'class_notes'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(255))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'uploaded_by_id': self.uploaded_by_id,
            'uploaded_at': self.uploaded_at.isoformat()
        }
