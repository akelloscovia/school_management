# MySQL Setup Guide

## MySQL Installation

### Windows
1. Download MySQL from: https://dev.mysql.com/downloads/mysql/
2. Run the installer and follow the setup wizard
3. Configure MySQL Server (port 3306 is default)
4. Create a MySQL user (default: root)

### macOS
```bash
brew install mysql
mysql.server start
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

---

## Create Database and User

### 1. Connect to MySQL
```bash
mysql -u root -p
# Enter your root password
```

### 2. Create Database
```sql
CREATE DATABASE school_management;
```

### 3. Create Application User (Optional but Recommended)
```sql
CREATE USER 'school_user'@'localhost' IDENTIFIED BY 'school_password123';
GRANT ALL PRIVILEGES ON school_management.* TO 'school_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## Configure Your Application

### Update .env File

```bash
# Copy example file
copy .env.example .env
```

Then edit `.env` with your MySQL credentials:

```
# For root user
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/school_management

# OR for application user
DATABASE_URL=mysql+pymysql://school_user:school_password123@localhost:3306/school_management

FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=your-secret-key-here
```

---

## Setup Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify MySQL Connection
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine.url)"
```

### 3. Initialize Database
```bash
python init_db.py
```

You should see:
```
Creating database tables...
Database tables created successfully!
```

### 4. Seed Sample Data (Optional)
```bash
python seed_data.py
```

You should see:
```
Seeding database...
Created role: admin
Created role: teacher
...
Database seeding completed!
```

### 5. Run the Application
```bash
python run.py
```

Server starts at: **http://localhost:5000**

---

## Verify Database Tables

### Check tables were created:
```bash
mysql -u root -p school_management -e "SHOW TABLES;"
```

You should see tables like:
```
+---------------------------+
| Tables_in_school_management |
+---------------------------+
| announcement              |
| attendance                |
| attendance_summary        |
| classes                   |
| marks                     |
| messages                  |
| roles                     |
| student_parents           |
| students                  |
| subjects                  |
| term_reports              |
| users                     |
+---------------------------+
```

### Check data:
```bash
mysql -u root -p school_management -e "SELECT * FROM roles;"
mysql -u root -p school_management -e "SELECT * FROM users;"
```

---

## Common Issues & Solutions

### Connection Error: "Access denied for user 'root'@'localhost'"
**Solution**: Check your MySQL password in `.env` file

```bash
# Test connection
mysql -u root -p -h localhost school_management
```

### Error: "No module named 'pymysql'"
**Solution**: Install the MySQL driver
```bash
pip install PyMySQL
```

### Error: "Can't connect to MySQL server"
**Solution**: Verify MySQL is running

**Windows**:
```bash
# Check if service is running
Get-Service MySQL80  # or your version

# Start service if stopped
Start-Service MySQL80
```

**macOS**:
```bash
mysql.server status
mysql.server start
```

**Linux**:
```bash
sudo systemctl status mysql
sudo systemctl start mysql
```

### Tables already exist error
**Solution**: Drop and recreate the database
```bash
mysql -u root -p -e "DROP DATABASE school_management; CREATE DATABASE school_management;"
python init_db.py
python seed_data.py
```

---

## MySQL Performance Tips

### 1. Create Indexes
```sql
USE school_management;

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_students_admission ON students(admission_number);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_marks_student ON marks(student_id);
```

### 2. Enable Binary Logging (For backups)
Edit MySQL config file (my.ini on Windows):
```
[mysqld]
log-bin=mysql-bin
binlog_format=row
```

### 3. Optimize Queries
- Use pagination for large datasets
- Add indexes on frequently searched fields
- Monitor slow queries

---

## Backup & Restore

### Backup Database
```bash
mysqldump -u root -p school_management > backup_school.sql
```

### Restore Database
```bash
mysql -u root -p school_management < backup_school.sql
```

### Automated Backup (Windows - Task Scheduler)
```batch
@echo off
set BACKUP_DIR=C:\backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
mysqldump -u root -pYOUR_PASSWORD school_management > %BACKUP_DIR%\backup_%TIMESTAMP%.sql
```

---

## Production Deployment

### MySQL Production Configuration

1. **Use Strong Passwords**
```bash
# Generate secure password
openssl rand -base64 32
```

2. **Create Restricted User**
```sql
CREATE USER 'app_user'@'192.168.1.100' IDENTIFIED BY 'STRONG_PASSWORD_HERE';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER ON school_management.* TO 'app_user'@'192.168.1.100';
FLUSH PRIVILEGES;
```

3. **Update Production .env**
```
FLASK_ENV=production
DATABASE_URL=mysql+pymysql://app_user:STRONG_PASSWORD@database_server:3306/school_management
JWT_SECRET_KEY=GENERATE_STRONG_SECRET_KEY
```

4. **Enable SSL**
```sql
GRANT ALL ON school_management.* TO 'app_user'@'192.168.1.100' REQUIRE SSL;
FLUSH PRIVILEGES;
```

---

## Monitor Database

### Check Database Size
```bash
mysql -u root -p -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb FROM information_schema.tables WHERE table_schema = 'school_management';"
```

### Monitor Connections
```bash
mysql -u root -p -e "SHOW PROCESSLIST;"
```

### Check Slow Queries
```bash
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query_log%';"
```

---

## MySQL Commands Reference

```bash
# Connect to MySQL
mysql -u root -p

# List all databases
SHOW DATABASES;

# Use a database
USE school_management;

# Show all tables
SHOW TABLES;

# Show table structure
DESCRIBE users;

# Show table creation SQL
SHOW CREATE TABLE users;

# Count rows
SELECT COUNT(*) FROM users;

# Show current user
SELECT USER();

# Show MySQL version
SELECT VERSION();
```

---

## Next Steps

1. ✅ Install MySQL
2. ✅ Create database and user
3. ✅ Configure `.env` file
4. ✅ Install Python dependencies
5. ✅ Initialize database
6. ✅ Seed sample data
7. ✅ Run the application
8. 🚀 Test API endpoints

Your Flask application is now connected to MySQL!
