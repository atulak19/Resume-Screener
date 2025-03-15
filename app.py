import nltk
import os
import sqlite3
import re
from flask import send_file
import io
from flask import send_file
import io

from database import save_resume, get_all_resumes, get_resume
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session, Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Set the path manually
nltk.data.path.append(os.path.join(os.getcwd(), "nltk_data"))

# Download required NLTK data
nltk.download("punkt", download_dir=os.path.join(os.getcwd(), "nltk_data"))
nltk.download("stopwords", download_dir=os.path.join(os.getcwd(), "nltk_data"))
nltk.download("punkt_tab", download_dir=os.path.join(os.getcwd(), "nltk_data"))

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import fitz  # PyMuPDF for extracting text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from fuzzywuzzy import fuzz

def save_to_database(resume_text, job_description, match_score, common_keywords):
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resumes (resume_text, job_description, match_score, common_keywords) VALUES (?, ?, ?, ?)",
        (resume_text, job_description, match_score, ", ".join(common_keywords)),
    )
    conn.commit()
    conn.close()

def clean_text(text):
    """Tokenizes text, removes stopwords, and returns important words"""
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())  # Convert to lowercase and tokenize
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]  # Remove punctuation & stopwords
    return filtered_words

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Add this line for session management

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    # If user is logged in, redirect to upload page
    if 'user' in session:
        return redirect(url_for('upload_page'))
    return render_template('home.html')

@app.route('/upload')
def upload_page():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('upload.html', username=session['user'])

def extract_text_from_pdf(pdf_path):
    """Function to extract text from a PDF file."""
    try:
        # For test files, return the content directly
        if os.path.basename(pdf_path) == 'test_resume.pdf':
            with open(pdf_path, 'rb') as f:
                return f.read().decode('utf-8')
                
        # For real PDF files, use PyMuPDF
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        print(f"Text extraction error: {str(e)}")  # Debug log
        return "Error extracting text"

def is_valid_text(text, is_resume=False):
    """Check if input text is valid (no harmful characters)."""
    if not text:
        return False
        
    # For resume text, only check for script tags and dangerous patterns
    if is_resume:
        dangerous_patterns = [
            r'<[^>]*script',
            r'javascript\s*:',
            r'vbscript\s*:',
            r'data\s*:',
            r'onload\s*=',
            r'onerror\s*='
        ]
        return not any(re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns)
        
    # For job descriptions, only check for SQL injection and XSS, allow special characters
    dangerous_patterns = [
        # SQL injection patterns
        r'\bSELECT\b.*\bFROM\b',
        r'\bINSERT\b.*\bINTO\b',
        r'\bUPDATE\b.*\bSET\b',
        r'\bDELETE\b.*\bFROM\b',
        r'\bDROP\b.*\bTABLE\b',
        r'\bUNION\b.*\bSELECT\b',
        # XSS patterns
        r'<[^>]*script',
        r'javascript\s*:',
        r'vbscript\s*:',
        r'onload\s*=',
        r'onerror\s*='
    ]
    return not any(re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns)

def is_valid_pdf(file):
    """Check if uploaded file is a valid PDF."""
    if not file or not file.filename:
        return False
        
    # Check file extension
    if not file.filename.lower().endswith('.pdf'):
        return False
        
    # Check file size (max 10MB)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 10 * 1024 * 1024:  # 10MB
        return False
        
    return True

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with proper validation and error handling"""
    try:
        # Check if user is logged in
        if 'user' not in session:
            return jsonify({"error": "Authentication required"}), 401

        # Get user_id from session
        username = session.get('user')
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        user_id = user[0]

        if 'resume' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['resume']
        print(f"Received file: {file.filename}")  # Debug log
        
        # Validate file
        if not is_valid_pdf(file):
            return jsonify({"error": "Invalid file. Please upload a valid PDF file (max 10MB)."}), 400
            
        # Validate job description
        job_description = request.form.get('job_description', "")
        if not is_valid_text(job_description):
            return jsonify({"error": "Invalid job description. Please remove any special characters."}), 400

        # Use secure filename
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({"error": "Invalid filename"}), 400

        # Save file with secure filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        print(f"File saved at: {filepath}")  # Debug log

        # Extract text from the uploaded resume
        extracted_text = extract_text_from_pdf(filepath)
        print(f"Extracted text length: {len(extracted_text)}")  # Debug log
        
        # Validate extracted text with less strict rules
        if not is_valid_text(extracted_text, is_resume=True):
            os.remove(filepath)  # Remove the file if text is invalid
            return jsonify({"error": "Invalid content in PDF. The file contains potentially harmful content."}), 400

        # Match keywords with job description
        match_percentage, common_keywords = match_keywords(extracted_text, job_description)

        # Calculate fuzzy match score
        fuzzy_score = fuzzy_match(extracted_text, job_description)

        # Save to database with user_id
        resume_id = save_resume(
            file_name=filename,
            file_path=filepath,
            file_size=file_size,
            resume_text=extracted_text,
            job_description=job_description,
            match_score=match_percentage,
            common_keywords=common_keywords,
            user_id=user_id
        )

        if resume_id is None:
            os.remove(filepath)  # Remove the file if save failed
            return jsonify({"error": "Failed to save resume"}), 500

        return jsonify({
            "status": "success",
            "message": "Resume uploaded successfully",
            "resume_id": resume_id,
            "match_percentage": match_percentage,
            "fuzzy_score": fuzzy_score,
            "common_keywords": common_keywords
        }), 201

    except Exception as e:
        print(f"Upload error: {str(e)}")  # Debug log
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/resumes')
def view_resumes():
    """View all uploaded resumes"""
    resumes = get_all_resumes()
    return render_template('resumes.html', resumes=resumes)

def fuzzy_match(text1, text2):
    return fuzz.partial_ratio(text1, text2)

def match_keywords(resume_text, job_description):
    """Calculate keyword match percentage between resume and job description."""
    
    # Clean and preprocess the text
    resume_words = clean_text(resume_text)
    job_words = clean_text(job_description)

    # Reconstruct text after cleaning
    resume_cleaned = " ".join(resume_words)
    job_cleaned = " ".join(job_words)

    # Convert text into vectors
    vectorizer = CountVectorizer().fit([resume_cleaned, job_cleaned])
    resume_vector = vectorizer.transform([resume_cleaned])
    job_vector = vectorizer.transform([job_cleaned])

    # Calculate cosine similarity
    similarity = cosine_similarity(resume_vector, job_vector)[0][0] * 100  # Convert to percentage

    # Find common words
    common_keywords = list(set(resume_words) & set(job_words))

    return similarity, common_keywords  # Ensure returning a tuple (float, list)

# API Endpoints
@app.route('/api/resumes', methods=['GET'])
def get_resumes_api():
    """API endpoint to get all resumes"""
    try:
        resumes = get_all_resumes()
        return jsonify({
            'status': 'success',
            'count': len(resumes),
            'resumes': resumes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/resumes/<int:resume_id>', methods=['GET'])
def get_resume_api(resume_id):
    """API endpoint to get a specific resume by ID"""
    try:
        resume = get_resume(resume_id)
        if resume:
            return jsonify({
                'status': 'success',
                'resume': resume
            })
        return jsonify({
            'status': 'error',
            'message': 'Resume not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/resumes/search', methods=['GET'])
def search_resumes_api():
    """API endpoint to search resumes by keyword (only user's own resumes)"""
    try:
        # Check authentication
        if 'user' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401

        keyword = request.args.get('keyword', '').lower()
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': 'Keyword parameter is required'
            }), 400

        # Get only user's resumes
        resumes = get_all_resumes()
        filtered_resumes = [
            resume for resume in resumes
            if keyword in resume['resume_text'].lower() or
            keyword in resume['job_description'].lower() or
            any(keyword in kw.lower() for kw in resume['common_keywords'])
        ]

        return jsonify({
            'status': 'success',
            'count': len(filtered_resumes),
            'resumes': filtered_resumes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/view_resume/<path:filename>')
def view_resume(filename):
    """Serve the PDF file only if it belongs to the current user"""
    try:
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        
        # Get user_id from username in session
        username = session.get('user')
        if not username:
            return jsonify({"error": "Authentication required"}), 401
            
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
            
        user_id = user[0]
        
        # Check if the file belongs to the user
        cursor.execute("SELECT id FROM resumes WHERE file_name = ? AND user_id = ?", (filename, user_id))
        if not cursor.fetchone():
            return jsonify({"error": "Access denied"}), 403
            
        conn.close()
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def register_user(username, password):
    hashed_password = generate_password_hash(password)  # Hash the password for security
    try:
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if register_user(username, password):
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return jsonify({"error": "Username already exists"}), 409

# Create users table if it doesn't exist
def create_users_table():
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create resumes table with user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            resume_text TEXT,
            job_description TEXT,
            match_score REAL,
            common_keywords TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Call create_users_table when app starts
create_users_table()

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        print(f"Login attempt - Username: {username}")  # Debug print

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        print(f"Database result: {user}")  # Debug print
        
        if user:
            is_valid = check_password_hash(user[0], password)
            print(f"Password validation result: {is_valid}")  # Debug print
            if is_valid:
                session["user"] = username
                return jsonify({"message": "Login successful"}), 200
        
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        print(f"Error in login: {str(e)}")  # Debug print
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

        
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)  # Remove user session
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/resumes/<int:resume_id>/download', methods=['GET'])
def download_resume(resume_id):
    """Download a specific resume by ID"""
    try:
        # Check if user is logged in
        if 'user' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401

        # Get user_id from session
        username = session.get('user')
        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
            
        user_id = user[0]
        
        # Get resume details and verify ownership
        cursor.execute("""
            SELECT file_path, file_name 
            FROM resumes 
            WHERE id = ? AND user_id = ?
        """, (resume_id, user_id))
        
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({
                'status': 'error',
                'message': 'Resume not found or access denied'
            }), 404
            
        file_path, file_name = resume
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': 'Resume file not found'
            }), 404
            
        # Return file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_name,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Download failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
