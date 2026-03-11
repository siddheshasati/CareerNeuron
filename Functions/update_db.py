import sqlite3

# Connect to your existing database
conn = sqlite3.connect("portal.db")
cursor = conn.cursor()

# List of all the new columns we added today
new_columns = [
    ("dob", "TEXT"),
    ("gender", "TEXT"),
    ("state", "TEXT"),
    ("city", "TEXT"),
    ("education", "TEXT"),
    ("experience", "TEXT"),
    ("ai_suggestions", "TEXT"),
    ("resume_path", "TEXT")
]

for col_name, col_type in new_columns:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    except sqlite3.OperationalError:
        print(f"Column '{col_name}' already exists.")

conn.commit()
conn.close()
print("Database update complete! You can now run your main app.")