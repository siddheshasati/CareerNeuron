import sqlite3
import os

def get_db():
    # Ensure the directory for the database exists
    if not os.path.exists("db"):
        os.makedirs("db")
    conn = sqlite3.connect("db/portal_web.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row # This allows fetching data by column name
    return conn

def init_db():
    # Create upload directory for resumes
    if not os.path.exists("uploads/resumes"):
        os.makedirs("uploads/resumes")
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE, mobile TEXT, password TEXT, role TEXT,
                        profile_completed INTEGER DEFAULT 0, full_name TEXT,
                        dob TEXT, gender TEXT, country TEXT, state TEXT, city TEXT,
                        pincode TEXT, address TEXT, profile_pic TEXT,
                        education TEXT, experience TEXT, ai_suggestions TEXT, resume_path TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT, company TEXT, location TEXT, link TEXT)''')
    # ... your existing CREATE TABLE queries ...
    conn.commit()
    conn.close()