import sqlite3
import datetime

DB_NAME = "startup_fund.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():

    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    # Images
    c.execute("""
    CREATE TABLE IF NOT EXISTS fund_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        image BLOB,
        prediction TEXT,
        confidence REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def register_user(username,password):

    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users VALUES (?,?)",
            (username,password)
        )
        conn.commit()
        return True

    except:
        return False

def check_login(username,password):

    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )

    result = c.fetchone()
    conn.close()

    return result is not None

def save_item(username,image_bytes,prediction,confidence):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT INTO fund_items
    (username,image,prediction,confidence,timestamp)
    VALUES (?,?,?,?,?)
    """,(
        username,
        image_bytes,
        prediction,
        confidence,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
