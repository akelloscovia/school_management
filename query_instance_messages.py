import sqlite3
import os

path = os.path.abspath('instance/school_management.db')
print('db_path', path)
print('exists', os.path.exists(path))
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cur.fetchall()]
print('tables:', tables)
if 'messages' in tables:
    cur.execute('SELECT id, sender_id, recipient_id, subject, body, is_read, created_at FROM messages ORDER BY id DESC LIMIT 20')
    rows = cur.fetchall()
    print('rows', len(rows))
    for row in rows:
        print(row)
else:
    print('messages table not found')
conn.close()
