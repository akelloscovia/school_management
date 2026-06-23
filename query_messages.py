import sqlite3

conn = sqlite3.connect('school_management.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cur.fetchall()]
print('db_path', 'school_management.db')
print('tables:', tables)
if 'messages' in tables:
    cur.execute('SELECT id, sender_id, recipient_id, subject, body, is_read, created_at FROM messages ORDER BY id DESC LIMIT 10')
    rows = cur.fetchall()
    print('rows', len(rows))
    for row in rows:
        print(row)
else:
    print('messages table not found')
conn.close()
