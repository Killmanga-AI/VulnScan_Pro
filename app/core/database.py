import sqlite3
import os

def init_db():
    """Initialize database with tables"""
    db_path = "data/database/vulnscan.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Customer table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        scan_credits INTEGER DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #Scans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        target_url TEXT,
        status TEXT,
        vulnerabilities_found INTEGER DEFAULT 0,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized")

if __name__ == "__main__":
    init_db()