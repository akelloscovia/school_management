"""Create the MySQL database specified in DATABASE_URL without needing the mysql CLI.
Usage: python create_db.py
It reads DATABASE_URL from the environment or .env file.
"""
from sqlalchemy import create_engine, text
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    print('DATABASE_URL not set in environment or .env')
    raise SystemExit(1)

parsed = urlparse(DB_URL)

# Extract database name (path) and construct base URL without database
db_name = parsed.path.lstrip('/') if parsed.path else ''
if not db_name:
    print('No database name found in DATABASE_URL; please include one.')
    raise SystemExit(1)

base_url = f"{parsed.scheme}://{parsed.username or ''}"
if parsed.password:
    base_url += f":{parsed.password}"
base_url += f"@{parsed.hostname or 'localhost'}"
if parsed.port:
    base_url += f":{parsed.port}"
base_url += "/"

print(f"Connecting to server to create database '{db_name}'...")

try:
    engine = create_engine(base_url)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
    print('Database created or already exists.')
except Exception as e:
    print('Error creating database:', e)
    raise SystemExit(1)
