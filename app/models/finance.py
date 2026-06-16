from app import db
from datetime import datetime


def generate_receipt_number():
    return f"RCPT{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{db.session.query(db.func.count(FeePayment.id)).scalar() + 1:04d}"


class FeePayment(db.Model):
    """Student fee payment record"""
    __tablename__ = 'fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    receipt_number = db.Column(db.String(100), unique=True, nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    term = db.Column(db.String(20))
    description = db.Column(db.Text)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat(),
            'payment_method': self.payment_method,
            'receipt_number': self.receipt_number,
            'academic_year': self.academic_year,
            'term': self.term,
            'description': self.description,
            'recorded_by_id': self.recorded_by_id
        }


class Expense(db.Model):
    """Finance expense record"""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'expense_date': self.expense_date.isoformat(),
            'description': self.description,
            'recorded_by_id': self.recorded_by_id
        }
