import sqlite3
import pandas as pd

# ✅ Initialize the database with required tables
def init_db():
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            amount REAL,
            type TEXT,
            description TEXT,
            date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# ✅ Add a new income/expense entry
def add_entry(user, amount, entry_type, description, date):
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO budget (user, amount, type, description, date) VALUES (?, ?, ?, ?, ?)",
        (user, amount, entry_type, description, date)
    )
    conn.commit()
    conn.close()

# ✅ Get user data
def get_data(user):
    conn = sqlite3.connect("budget_data.db")
    df = pd.read_sql_query("SELECT * FROM budget WHERE user=?", conn, params=(user,))
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    return df

# ✅ Create a new user
def create_user(username, password):
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

# ✅ Check if user credentials are valid
def check_user(username, password):
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None
