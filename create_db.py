import sqlite3
import os

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Create a new SQLite database if it doesn't exist
db_path = "data/ticket-sales.db"

# Connect to SQLite (this will create the file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the sales table with the schema
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        customer_name TEXT,
        amount REAL,
        date TEXT
    )
""")

# Insert some sample data
cursor.executemany("""
    INSERT INTO sales (customer_name, amount, date) VALUES (?, ?, ?)
""", [
    ("John Doe", 150.75, '2025-01-10'),
    ("Jane Smith", 200.50, '2025-01-11'),
    ("Robert Brown", 120.25, '2025-01-12')
])

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created and sample data inserted.")
