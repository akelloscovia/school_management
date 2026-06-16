import os
import sqlite3

path = os.path.join(os.getcwd(), 'school_management.db')
print('DB exists:', os.path.exists(path), path)

if not os.path.exists(path):
    raise SystemExit('Database file not found')

conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('tables:', tables)
for table in ['user', 'users', 'User', 'Users']:
    if table in tables:
        try:
            cur.execute(f"SELECT id, first_name, last_name, email, role_id, is_active FROM {table} LIMIT 10")
            rows = cur.fetchall()
            if rows:
                print('found rows in', table)
                for row in rows:
                    print(row)
        except Exception as e:
            print('error reading', table, e)
conn.close()
