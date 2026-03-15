import sqlite3
import hashlib
import os

DATABASE_PATH = "skin_disease_db.sqlite"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                contact_email TEXT,
                contact_phone TEXT,
                address TEXT,
                experience_years INTEGER,
                diseases_treated TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                image_name TEXT,
                predicted_disease TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prediction_id INTEGER,
                rating INTEGER,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_admin)
                VALUES (?, ?, ?, ?)
            ''', ("admin", "admin@skindisease.com", admin_password, True))
        
        # Add some sample doctors if table is empty
        cursor.execute("SELECT COUNT(*) FROM doctors")
        if cursor.fetchone()[0] == 0:
            sample_doctors = [
                ("Dr. Sarah Johnson", "Dermatology & Oncology", "sarah.johnson@hospital.com", "555-0123", "123 Medical Center Dr", 15, "Melanoma, Squamous Cell Carcinoma, Actinic Keratosis"),
                ("Dr. Michael Chen", "Dermatopathology", "michael.chen@clinic.com", "555-0124", "456 Health Plaza", 12, "Melanoma, Seborrheic Keratosis, Dermatofibroma"),
                ("Dr. Emily Davis", "Dermatology", "emily.davis@skincare.com", "555-0125", "789 Beauty Ave", 8, "Actinic Keratosis, Seborrheic Keratosis, Dermatofibroma"),
                ("Dr. Robert Wilson", "Oncology & Dermatology", "robert.wilson@childcare.com", "555-0126", "321 Kids Health St", 10, "Squamous Cell Carcinoma, Melanoma, Actinic Keratosis"),
                ("Dr. Lisa Martinez", "Mohs Surgery", "lisa.martinez@mohscenter.com", "555-0127", "555 Surgical Suite", 18, "Squamous Cell Carcinoma, Melanoma, Actinic Keratosis"),
                ("Dr. David Park", "Dermatology", "david.park@dermclinic.com", "555-0128", "888 Skin Care Ave", 7, "Dermatofibroma, Seborrheic Keratosis, Actinic Keratosis")
            ]
            
            for doctor in sample_doctors:
                cursor.execute('''
                    INSERT INTO doctors (name, specialization, contact_email, contact_phone, address, experience_years, diseases_treated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', doctor)
        
        conn.commit()
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.close()
    except Exception as e:
        print(f"General error: {e}")
        if 'conn' in locals():
            conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()