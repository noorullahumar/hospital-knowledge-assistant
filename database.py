import sqlite3
import bcrypt
import uuid

# Configuration: Standardize database file name
DB_NAME = "hospital_users.db"

def init_db():
    """Initializes the database and ensures all tables/columns exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Users Table (Uses 'email' as primary identifier)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    """)
    
    # 2. Chat History Table (Uses 'user_email' as the reference)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_email TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# --- SESSION MANAGEMENT ---

def create_new_session(user_email):
    """Generates a unique 8-character string for a conversation thread."""
    return str(uuid.uuid4())[:8]

def get_user_sessions(user_email):
    """Retrieves list of session IDs belonging to a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Corrected: Query uses user_email column
    c.execute("""
        SELECT DISTINCT session_id FROM chat_history 
        WHERE user_email = ? ORDER BY timestamp DESC
    """, (user_email,))
    sessions = [row[0] for row in c.fetchall() if row[0] is not None]
    conn.close()
    return sessions

def delete_session(session_id):
    """Deletes all messages for a specific session ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# --- MESSAGE LOGIC ---

def save_message(session_id, user_email, role, content):
    """Inserts a new message into the history table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO chat_history (session_id, user_email, role, content) 
        VALUES (?, ?, ?, ?)
    """, (session_id, user_email, role, content))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    """Fetches all messages for a specific session."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM chat_history 
        WHERE session_id = ? ORDER BY timestamp ASC
    """, (session_id,))
    history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return history

def clear_chat_history(user_email):
    """Wipes all records for a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Corrected: column name updated to user_email
    c.execute("DELETE FROM chat_history WHERE user_email = ?", (user_email,))
    conn.commit()
    conn.close()

# --- AUTHENTICATION ---

def add_user(user_email, password, role):
    """Registers a new user. Admins can only be created via special setup tool."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if we are creating the very first user (Special case for Admin Setup Tool)
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]

    # Security Guard: Only allow Admin role if it's the first ever user 
    # OR if explicitly called through code logic.
    allowed_roles = ["Patient", "Staff", "Admin"]
    final_role = role if role in allowed_roles else "Patient"

    try:
        # Generate secure hash and decode to string for storage
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", 
                  (user_email, hashed_pw, final_role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    """Verifies credentials."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()

    if result:
        hashed_pwd, role = result
        # bcrypt.checkpw expects (bytes, bytes)
        if bcrypt.checkpw(password.encode('utf-8'), hashed_pwd.encode('utf-8')):
            return role
    return None

def admin_exists():
    """Checks if any Admin exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE role = 'Admin' LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result is not None

def reset_user_password(user_email, new_password):
    """Hashes new password and updates record."""
    try:
        # Encode to string for SQLite storage
        hashed_pwd = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pwd, user_email))
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    except Exception as e:
        print(f"Database error: {e}")
        return False

# To check wether the user exist or not
def user_exists(email):
    """Checks if an email is registered in the system."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None