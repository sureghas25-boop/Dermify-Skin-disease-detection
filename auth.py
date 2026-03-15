import sqlite3
import hashlib
from database import get_db_connection, hash_password

def authenticate_user(username, password):
    """Authenticate user login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def register_user(username, email, password):
    """Register new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def is_admin(username):
    """Check if user is admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT is_admin FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    return result and result[0]

def get_user_id(username):
    """Get user ID by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None
