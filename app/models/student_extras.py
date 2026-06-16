from app import db
from datetime import datetime


class StudentDocument(db.Model):
    """Student document upload metadata"""
    __tablename__ = 'student_documents'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'document_type': self.document_type,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'uploaded_by_id': self.uploaded_by_id,
            'uploaded_at': self.uploaded_at.isoformat()
        }


class StudentTransfer(db.Model):
    """Student transfer record model"""
    __tablename__ = 'student_transfers'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    from_class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    to_class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    parent_contact = db.Column(db.String(100))
    medical_info = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    comments = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'from_class_id': self.from_class_id,
            'to_class_id': self.to_class_id,
            'transfer_date': self.transfer_date.isoformat(),
            'reason': self.reason,
            'status': self.status,
            'parent_contact': self.parent_contact,
            'medical_info': self.medical_info,
            'photo_url': self.photo_url,
            'comments': self.comments
        }


class PromotionHistory(db.Model):
    """Student promotion history model"""
    __tablename__ = 'promotion_history'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    from_class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    to_class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    promoted_at = db.Column(db.DateTime, default=datetime.utcnow)
    promoted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    remarks = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'from_class_id': self.from_class_id,
            'to_class_id': self.to_class_id,
            'promoted_at': self.promoted_at.isoformat(),
            'promoted_by_id': self.promoted_by_id,
            'remarks': self.remarks
        }
