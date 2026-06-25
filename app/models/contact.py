from datetime import datetime
from app import db


class ContactInfo(db.Model):
    __tablename__ = 'contact_info'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(100))
    address = db.Column(db.Text)
    map_embed_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number,
            'address': self.address,
            'map_embed_url': self.map_embed_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'reply': self.reply,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
