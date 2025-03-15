import sqlite3
from datetime import datetime
from flask import session

def create_table():
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Creating a table to store resume data with file path and user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT,
            file_path TEXT,
            file_size INTEGER,
            resume_text TEXT,
            job_description TEXT,
            match_score REAL,
            common_keywords TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def save_resume(file_name, file_path, file_size, resume_text, job_description, match_score, common_keywords, user_id):
    """Save resume details to database with user_id"""
    try:
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resumes (user_id, file_name, file_path, file_size, resume_text, job_description, match_score, common_keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, file_name, file_path, file_size, resume_text, job_description, match_score, ", ".join(common_keywords)))
        
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return resume_id
    except Exception as e:
        print(f"Error saving resume: {str(e)}")
        return None

def get_resume(resume_id):
    """Get a specific resume, ensuring it belongs to the current user"""
    try:
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        
        # Get user_id from username in session
        username = session.get('user')
        if not username:
            return None
            
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return None
            
        user_id = user[0]
        
        cursor.execute("""
            SELECT id, file_name, file_path, file_size, resume_text, job_description, match_score, common_keywords, uploaded_at
            FROM resumes 
            WHERE id = ? AND user_id = ?
        """, (resume_id, user_id))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        resume = {
            'id': row[0],
            'file_name': row[1],
            'file_path': row[2],
            'file_size': row[3],
            'resume_text': row[4],
            'job_description': row[5],
            'match_score': row[6],
            'common_keywords': row[7].split(', ') if row[7] else [],
            'uploaded_at': row[8]
        }
        
        conn.close()
        return resume
    except Exception as e:
        print(f"Error getting resume: {str(e)}")
        return None

def get_all_resumes():
    """Get all resumes for the current user"""
    try:
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        
        # Get user_id from username in session
        username = session.get('user')
        if not username:
            return []
            
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return []
            
        user_id = user[0]
        
        cursor.execute("""
            SELECT id, file_name, file_path, file_size, resume_text, job_description, match_score, common_keywords, uploaded_at
            FROM resumes 
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
        """, (user_id,))
        
        resumes = []
        for row in cursor.fetchall():
            resumes.append({
                'id': row[0],
                'file_name': row[1],
                'file_path': row[2],
                'file_size': row[3],
                'resume_text': row[4],
                'job_description': row[5],
                'match_score': row[6],
                'common_keywords': row[7].split(', ') if row[7] else [],
                'uploaded_at': row[8]
            })
        
        conn.close()
        return resumes
    except Exception as e:
        print(f"Error getting resumes: {str(e)}")
        return []

# Run this file manually once to create the table
if __name__ == "__main__":
    create_table()
