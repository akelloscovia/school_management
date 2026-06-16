from app import db
from datetime import datetime


class Book(db.Model):
    """Library book model"""
    __tablename__ = 'library_books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150))
    isbn = db.Column(db.String(50), unique=True)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    category = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'category': self.category,
            'publisher': self.publisher,
            'created_at': self.created_at.isoformat()
        }


class BorrowRecord(db.Model):
    """Library borrow/return record"""
    __tablename__ = 'borrow_records'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('library_books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    borrowed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    returned_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='borrowed')

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'student_id': self.student_id,
            'borrowed_by_id': self.borrowed_by_id,
            'borrow_date': self.borrow_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'returned_date': self.returned_date.isoformat() if self.returned_date else None,
            'status': self.status
        }
