from app import db
from datetime import datetime


class BusRoute(db.Model):
    """Bus route model"""
    __tablename__ = 'bus_routes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    driver_name = db.Column(db.String(150))
    driver_phone = db.Column(db.String(50))
    route_description = db.Column(db.Text)
    capacity = db.Column(db.Integer, default=50)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'route_description': self.route_description,
            'capacity': self.capacity,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }


class BoardingAssignment(db.Model):
    """Student boarding assignment to a bus route"""
    __tablename__ = 'boarding_assignments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    bus_route_id = db.Column(db.Integer, db.ForeignKey('bus_routes.id'), nullable=False)
    boarding_point = db.Column(db.String(255))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'bus_route_id': self.bus_route_id,
            'boarding_point': self.boarding_point,
            'assigned_at': self.assigned_at.isoformat(),
            'active': self.active
        }


class Dormitory(db.Model):
    """Dormitory building model"""
    __tablename__ = 'dormitories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    block = db.Column(db.String(100))
    capacity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'block': self.block,
            'capacity': self.capacity,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


class DormitoryAllocation(db.Model):
    """Dormitory allocation record"""
    __tablename__ = 'dormitory_allocations'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    dormitory_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'), nullable=False)
    room_number = db.Column(db.String(50))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'dormitory_id': self.dormitory_id,
            'room_number': self.room_number,
            'assigned_at': self.assigned_at.isoformat(),
            'active': self.active
        }
