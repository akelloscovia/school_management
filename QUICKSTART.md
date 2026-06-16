# Quick Start Guide

## Installation & Setup

### 1. Create Virtual Environment
```bash
cd c:\Users\HP\Desktop\mgnt
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
copy .env.example .env
```

Then edit `.env` with your configuration.

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Seed Sample Data (Optional)
```bash
python seed_data.py
```

### 6. Run the Server
```bash
python run.py
```

Server starts at: **http://localhost:5000**

---

## Quick API Examples

### 1. Register a New User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@school.com",
    "password": "password123",
    "role_name": "student"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@school.com",
    "password": "password123"
  }'
```

Save the `access_token` from response.

### 3. Get Current User (Requires Token)
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Create a Student
```bash
curl -X POST http://localhost:5000/api/students \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Student",
    "email": "jane@school.com",
    "password": "password123",
    "date_of_birth": "2008-05-15",
    "gender": "Female",
    "class_id": 1
  }'
```

### 5. Get All Students
```bash
curl -X GET http://localhost:5000/api/students \
  -H "Authorization: Bearer TOKEN"
```

### 6. Record Attendance
```bash
curl -X POST http://localhost:5000/api/attendance \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "date": "2024-05-27",
    "status": "present"
  }'
```

### 7. Record Marks
```bash
curl -X POST http://localhost:5000/api/marks \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "subject_id": 1,
    "term": 1,
    "exam_type": "final",
    "marks_obtained": 85,
    "total_marks": 100
  }'
```

### 8. Generate Term Report
```bash
curl -X POST http://localhost:5000/api/reports/generate-term-report \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "term": 1,
    "academic_year": "2023/2024"
  }'
```

### 9. Get Student Performance
```bash
curl -X GET "http://localhost:5000/api/reports/performance-analytics/1" \
  -H "Authorization: Bearer TOKEN"
```

### 10. Send a Message
```bash
curl -X POST http://localhost:5000/api/communication/messages \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 2,
    "subject": "Meeting",
    "body": "Please come to office"
  }'
```

---

## Default Test Users

After running `seed_data.py`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@school.com | admin123 |
| Teacher | teacher@school.com | teacher123 |
| Student | student1@school.com | student123 |

---

## User Roles & Permissions

### Admin
- Full system access
- Manage all users and roles
- Configure system settings

### Teacher
- Record attendance
- Record and manage marks
- View student performance
- Create class announcements

### Student
- View own records
- View attendance and marks
- Track performance
- Send/receive messages

### Parent
- View child's records
- View child's attendance
- Receive announcements
- Message teachers

### Accountant
- View financial information
- Generate financial reports

---

## Common API Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    "id": 1,
    "name": "John Doe",
    ...
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "User not found"
}
```

### List Response with Pagination
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 50,
    "pages": 3,
    "current_page": 1,
    "per_page": 20
  }
}
```

---

## Pagination

Add these query parameters to any list endpoint:
- `page=1` - Page number (default: 1)
- `per_page=20` - Items per page (default: 20, max: 100)

Example:
```bash
http://localhost:5000/api/students?page=1&per_page=10
```

---

## Database Schema

The system uses the following main tables:

- **users** - User accounts
- **roles** - User roles (admin, teacher, student, parent, accountant)
- **students** - Student profiles
- **student_parents** - Parent information
- **classes** - Class/Grade information
- **subjects** - Subjects in each class
- **attendance** - Attendance records
- **marks** - Examination marks
- **term_reports** - Generated term reports
- **messages** - Direct messaging
- **announcements** - System announcements

---

## Configuration

Edit `.env` for development settings:

```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///school_management.db
JWT_SECRET_KEY=your-secret-key-change-in-production
```

For production, use PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost/school_management
JWT_SECRET_KEY=generate-a-strong-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
```

---

## File Structure Reference

```
mgnt/
├── app/                 # Main application
│   ├── models/         # Database models
│   ├── routes/         # API endpoints
│   ├── utils/          # Helper functions
│   └── __init__.py     # App factory
├── tests/              # Test files
├── run.py             # Start server
├── config.py          # Configuration
├── requirements.txt   # Dependencies
└── seed_data.py      # Sample data
```

---

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python run.py --port 5001
```

Or modify `.env`:
```
FLASK_PORT=5001
```

### Database Error
```bash
# Reinitialize database
python init_db.py
python seed_data.py
```

### Module Not Found
```bash
# Ensure virtual environment is activated
venv\Scripts\activate
pip install -r requirements.txt
```

### JWT Token Expired
- Generate a new token by logging in again
- Token expiration is configured in `config.py`

---

## Next Steps

1. **Frontend Integration**: Connect your frontend to the API
2. **Database Backup**: Set up regular database backups
3. **Security**: Update JWT_SECRET_KEY in production
4. **API Documentation**: Use Swagger UI (can be added)
5. **Testing**: Run test suite with `pytest`
6. **Deployment**: Deploy to production server

---

## Support

For issues or questions, refer to:
- README.md for detailed documentation
- API endpoint documentation in routes files
- Database model documentation in models files
