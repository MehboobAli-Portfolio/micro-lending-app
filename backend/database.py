import sqlite3
import os

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Finance Manager Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # 2. Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT
        )
    ''')
    
    # 3. Invoices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            invoice_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            amount_due REAL NOT NULL,
            status TEXT DEFAULT 'PENDING',
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # 4. Payment Links Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialization successful.")

if __name__ == '__main__':
    init_db()
