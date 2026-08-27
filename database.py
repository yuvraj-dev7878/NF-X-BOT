import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'trial.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            email TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_trial(user_id, username, email, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO trials (user_id, username, email, status) VALUES (?, ?, ?, ?)',
        (user_id, username, email, status)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    total = cursor.execute('SELECT COUNT(*) FROM trials').fetchone()[0]
    success = cursor.execute('SELECT COUNT(*) FROM trials WHERE status = "success"').fetchone()[0]
    failed = cursor.execute('SELECT COUNT(*) FROM trials WHERE status = "failed"').fetchone()[0]
    conn.close()
    return total, success, failed
