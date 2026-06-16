from app import db
from datetime import datetime


class Message(db.Model):
    """Direct messaging model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender': self.sender.to_dict(include_role=False),
            'recipient_id': self.recipient_id,
            'recipient': self.recipient.to_dict(include_role=False),
            'subject': self.subject,
            'body': self.body,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class Announcement(db.Model):
    """Announcements for groups/classes"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    announcement_type = db.Column(db.String(50), nullable=False)  # general, class, urgent
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime)
    
    created_by = db.relationship('User', backref='announcements')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_by': self.created_by.to_dict(include_role=False),
            'announcement_type': self.announcement_type,
            'class_id': self.class_id,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
