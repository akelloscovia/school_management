import os
import sqlite3

dirpath = os.path.abspath('.')
for root, dirs, files in os.walk(dirpath):
    for file in files:
        if file.endswith('.db'):
            path = os.path.join(root, file)
            try:
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
                found = cur.fetchone()
                print(path, 'messages table exists' if found else 'no messages table')
                conn.close()
            except Exception as e:
                print(path, 'error', e)
