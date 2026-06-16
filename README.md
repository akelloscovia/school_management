# School Management System - Flask Backend

A comprehensive Flask-based backend for a school management system that handles academic, administrative, and financial activities from one centralized platform.

## Features

### Core Functionality
- **Student Records Management**: Create, update, and manage student information
- **Attendance Tracking**: Automated attendance recording with status tracking
- **Examination Marks**: Record and process examination marks with automatic grading
- **Report Cards & Academic Reports**: Generate comprehensive term reports and performance analytics
- **User Authentication**: Secure JWT-based authentication with password hashing
- **Role-Based Access Control**: Five user roles with granular permissions
  - **Admin**: Full system access and configuration
  - **Teachers**: Attendance, marks, and student management
  - **Students**: View own records and performance
  - **Parents**: View child's academic progress
  - **Accountants**: Financial records management
- **Stakeholder Communication**: Direct messaging and announcements system
- **Performance Monitoring**: Track student performance trends over time

## System Architecture

```
mgnt/
├── app/
│   ├── models/           # Database models
│   ├── routes/           # API endpoints (blueprints)
│   ├── schemas/          # Data validation schemas (optional)
│   ├── utils/            # Helper functions and decorators
│   └── __init__.py       # App factory
├── migrations/           # Database migrations
├── tests/                # Test cases
├── config.py             # Configuration settings
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## User Roles & Permissions

### Admin
- Full access to all features
- User management (create, update, delete)
- System configuration
- Generate all reports
- View all announcements

### Teacher
- Record and manage attendance
- Record and manage student marks
- Create class announcements
- View student performance
- Message students and parents

### Student
- View own attendance records
- View own marks and reports
- Track personal performance
- Send messages
- Receive announcements

### Parent
- View child's attendance
- View child's marks and reports
- View child's performance trends
- Receive announcements
- Message teachers and school

### Accountant
- View financial information
- Generate financial reports
- Manage payment records

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
cd c:\Users\HP\Desktop\mgnt
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
```

5. **Initialize the database**
```bash
flask db init
flask db migrate
flask db upgrade
```

6. **Run the application**
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/refresh` - Refresh access token

### Users
- `GET /api/users` - Get all users (admin only)
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Deactivate user
- `GET /api/users/by-role/<role_name>` - Get users by role
- `POST /api/users/<id>/activate` - Activate user

### Students
- `GET /api/students` - Get all students
- `POST /api/students` - Create student (admin only)
- `GET /api/students/<id>` - Get student details
- `PUT /api/students/<id>` - Update student
- `GET /api/students/<id>/parents` - Get student's parents
- `POST /api/students/<id>/parents` - Add parent to student
- `GET /api/students/<id>/performance` - Get student performance summary

### Attendance
- `POST /api/attendance` - Record attendance
- `POST /api/attendance/bulk` - Bulk record attendance
- `GET /api/attendance/student/<id>` - Get student attendance records
- `GET /api/attendance/class/<class_id>/date/<date>` - Get class attendance by date
- `GET /api/attendance/summary/<student_id>` - Get attendance summary

### Marks
- `POST /api/marks` - Record marks
- `POST /api/marks/bulk` - Bulk record marks
- `GET /api/marks/student/<id>` - Get student marks
- `GET /api/marks/subject/<id>/term/<term>` - Get subject marks for term
- `PUT /api/marks/<id>` - Update marks

### Reports
- `POST /api/reports/generate-term-report` - Generate term report
- `GET /api/reports/student/<id>/term/<term>` - Get term report
- `GET /api/reports/student/<id>` - Get all reports for student
- `GET /api/reports/class/<id>/term/<term>` - Get class term reports
- `GET /api/reports/performance-analytics/<student_id>` - Get performance analytics

### Classes
- `GET /api/classes` - Get all classes
- `POST /api/classes` - Create class (admin only)
- `GET /api/classes/<id>` - Get class details
- `PUT /api/classes/<id>` - Update class
- `GET /api/classes/<id>/subjects` - Get class subjects
- `POST /api/classes/<id>/subjects` - Add subject to class
- `PUT /api/classes/subject/<id>` - Update subject

### Communication
- `POST /api/communication/messages` - Send message
- `GET /api/communication/messages/inbox` - Get inbox
- `GET /api/communication/messages/sent` - Get sent messages
- `GET /api/communication/messages/<id>` - Get message
- `DELETE /api/communication/messages/<id>` - Delete message
- `POST /api/communication/messages/<id>/mark-read` - Mark message as read
- `POST /api/communication/announcements` - Create announcement
- `GET /api/communication/announcements` - Get announcements
- `GET /api/communication/announcements/<id>` - Get announcement
- `PUT /api/communication/announcements/<id>` - Update announcement
- `DELETE /api/communication/announcements/<id>` - Delete announcement

## Database Models

### User
- User authentication and role management
- Fields: id, first_name, last_name, email, phone, password_hash, role_id, is_active, created_at, updated_at, last_login

### Student
- Student information and enrollment
- Fields: id, user_id, admission_number, date_of_birth, gender, address, class_id, enrollment_date, is_active

### Class
- Class/Grade information
- Fields: id, name, level, teacher_id, academic_year, max_capacity, description, created_at

### Subject
- Subject information
- Fields: id, name, code, class_id, description, credit_hours

### Attendance
- Attendance records with status tracking
- Fields: id, student_id, date, status, remarks, recorded_by_id, recorded_at

### Marks
- Examination marks with automatic grading
- Fields: id, student_id, subject_id, term, exam_type, marks_obtained, total_marks, percentage, grade, academic_year, recorded_by_id, recorded_at, updated_at

### Message
- Direct messaging between users
- Fields: id, sender_id, recipient_id, subject, body, is_read, created_at

### Announcement
- System and class announcements
- Fields: id, title, content, created_by_id, announcement_type, class_id, priority, created_at, expires_at

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/users
```

## Configuration

Configuration is managed through environment variables. Create a `.env` file based on `.env.example`:

```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///school_management.db
JWT_SECRET_KEY=your-secret-key
```

For production, use PostgreSQL and update the `DATABASE_URL`:
```
DATABASE_URL=postgresql://user:password@localhost/school_management
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback
flask db downgrade
```

### Using Flask Shell
```bash
flask shell
# Create a role
role = Role(name='admin', description='Administrator')
db.session.add(role)
db.session.commit()
```

## Performance Features

- **Pagination**: All list endpoints support pagination with `page` and `per_page` parameters
- **Indexing**: Database indexes on frequently queried fields
- **Caching Ready**: Structure supports adding caching layers
- **Bulk Operations**: Bulk endpoints for attendance and marks recording

## Security Features

- Password hashing with bcrypt
- JWT-based stateless authentication
- Role-based access control
- CORS protection
- Input validation on all endpoints
- SQL injection prevention with SQLAlchemy ORM

## Error Handling

All errors follow a consistent format:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE"
}
```

## Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Docker (Optional)
Create a `Dockerfile` for containerization.

## Future Enhancements

- [ ] Payment/Fee management module
- [ ] Exam scheduling system
- [ ] Student leave management
- [ ] Parent app notifications
- [ ] Advanced analytics dashboard
- [ ] Document storage (certificates, transcripts)
- [ ] Time-table management
- [ ] Library management
- [ ] Transport management
- [ ] SMS/Email notifications

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT License

## Support

For issues or questions, please contact the development team.

## Changelog

### Version 1.0.0 (Initial Release)
- Core authentication system
- Student management
- Attendance tracking
- Marks recording and grading
- Report generation
- Role-based access control
- Messaging system
- Announcement system
