import sqlite3
import bcrypt
import uuid

# Configuration: The name of the SQLite database file
DB_NAME = "hospital_users.db"

def init_db():
    """
    Initializes the database by creating the necessary tables if they don't exist.
    'users' table: Stores credentials and access levels.
    'chat_history' table: Stores messages linked by session_id and username.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create table for user accounts
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    
    # Create table for messages; session_id allows grouping messages into specific conversations
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  session_id TEXT, 
                  username TEXT, 
                  role TEXT, 
                  content TEXT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# --- SESSION MANAGEMENT ---

def create_new_session(username):
    """
    Generates a unique 8-character string to identify a specific conversation thread.
    Uses UUID for uniqueness.
    """
    return str(uuid.uuid4())[:8]

def get_user_sessions(username):
    """
    Retrieves a list of all unique session IDs belonging to a specific user.
    Ordered by the most recent message first.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # DISTINCT ensures we don't get duplicate IDs for every message in a chat
    c.execute("SELECT DISTINCT session_id FROM chat_history WHERE username = ? ORDER BY timestamp DESC", (username,))
    sessions = [row[0] for row in c.fetchall() if row[0] is not None]
    conn.close()
    return sessions

def delete_session(session_id):
    """
    Removes all messages associated with a specific session ID.
    Used for the '🗑️' button in the sidebar.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# --- MESSAGE LOGIC ---

def save_message(session_id, username, role, content):
    """
    Inserts a new message (either from User or AI) into the history table.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (session_id, username, role, content) VALUES (?, ?, ?, ?)", 
              (session_id, username, role, content))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    """
    Fetches all messages for a specific session to display them in the chat window.
    Ordered by timestamp so the conversation flows naturally.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    # Format as list of dicts for Streamlit's st.chat_message
    history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return history

def clear_chat_history(username):
    """
    Wipes all chat records for a user. Used for the 'Clear All' functionality.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# --- AUTHENTICATION ---
def add_user(username, password, role):
    """
    Registers a new user with hard-coded role security.
    Even if 'Admin' is passed, it defaults to 'Patient'.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # --- HARD SECURITY OVERRIDE ---
    # Only allow these roles to be created via the UI. 
    # If anything else (like 'Admin') is sent, force it to 'Patient'.
    allowed_public_roles = ["Patient", "Staff"]
    final_role = role if role in allowed_public_roles else "Patient"
    
    try:
        # Generate a secure hash of the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert using the validated final_role
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed_pw, final_role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Fails if the username already exists
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """
    Checks if the provided password matches the hashed password in the database.
    Returns the user's role (Admin/Staff/Patient) if successful.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    # Compare the provided password with the stored hash
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return result[1] # Return the role
    return None