from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import logging
import sys
from datetime import datetime
import traceback

# Import configuration
from config import config

# Initialize Flask app
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    return app

# Create app instance
app = create_app()

# Configure logging
def setup_logging():
    """Setup application logging"""
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/resume_analyzer.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Resume Analyzer startup')

setup_logging()

# Import analysis modules
try:
    import PyPDF2
    import docx
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import re
    import json
except ImportError as e:
    app.logger.error(f"Missing required dependency: {e}")
    sys.exit(1)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_file(file):
    """Validate uploaded file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"
    
    if file.content_length > app.config['MAX_CONTENT_LENGTH']:
        return False, f"File too large. Maximum size: {app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB"
    
    return True, "File is valid"

def safe_file_operation(operation, *args, **kwargs):
    """Safely execute file operations with error handling"""
    try:
        return operation(*args, **kwargs), None
    except Exception as e:
        app.logger.error(f"File operation error: {str(e)}")
        return None, str(e)

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    app.logger.warning(f"No text found on page {page_num} of PDF")
        return text.strip()
    except Exception as e:
        app.logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        app.logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            app.logger.error(f"Error reading TXT file with encoding fallback: {str(e)}")
            raise
    except Exception as e:
        app.logger.error(f"Error extracting text from TXT: {str(e)}")
        raise

def extract_resume_text(file_path, file_extension):
    """Extract text from resume based on file type"""
    extractors = {
        'pdf': extract_text_from_pdf,
        'docx': extract_text_from_docx,
        'txt': extract_text_from_txt
    }
    
    if file_extension not in extractors:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    return extractors[file_extension](file_path)

def extract_contact_info(text):
    """Extract contact information from text"""
    try:
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Phone patterns (more comprehensive)
        phone_patterns = [
            r'\b(?:\+?(\d{1,3}))?[-. (]?(\d{3})[-. )]?(\d{3})[-. ]?(\d{4})\b',
            r'\b(\d{3}[-. ]?\d{3}[-. ]?\d{4})\b',
            r'\b(\+1[-. ]?\d{3}[-. ]?\d{3}[-. ]?\d{4})\b'
        ]
        
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        phones = []
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phone = ''.join(filter(None, match))
                else:
                    phone = match
                if phone and len(phone) >= 10:
                    phones.append(phone)
        
        # Remove duplicates while preserving order
        unique_emails = list(dict.fromkeys(emails))
        unique_phones = list(dict.fromkeys(phones))
        
        return {
            'emails': unique_emails,
            'phones': unique_phones
        }
    except Exception as e:
        app.logger.error(f"Error extracting contact info: {str(e)}")
        return {'emails': [], 'phones': []}

def extract_skills(text):
    """Extract skills from resume text"""
    try:
        # Expanded skill databases
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'html', 'css', 'sql',
            'mongodb', 'git', 'docker', 'aws', 'azure', 'gcp', 'machine learning',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'flask',
            'django', 'angular', 'vue.js', 'typescript', 'c++', 'c#', '.net',
            'linux', 'ubuntu', 'windows', 'macos', 'api', 'rest', 'graphql',
            'mysql', 'postgresql', 'oracle', 'redis', 'kubernetes', 'jenkins',
            'gitlab', 'ci/cd', 'devops', 'microservices', 'spring boot', 'express',
            'jquery', 'bootstrap', 'tailwind', 'sass', 'webpack', 'babel',
            'php', 'laravel', 'ruby', 'rails', 'go', 'rust', 'swift', 'kotlin',
            'android', 'ios', 'flutter', 'react native', 'xamarin', 'cordova',
            'tableau', 'power bi', 'excel', 'word', 'powerpoint', 'outlook'
        ]
        
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
            'project management', 'time management', 'adaptability', 'creativity', 'analytical',
            'collaboration', 'interpersonal', 'presentation', 'negotiation', 'decision making',
            'organization', 'planning', 'delegation', 'mentoring', 'coaching', 'facilitation',
            'conflict resolution', 'strategic thinking', 'innovation', 'attention to detail',
            'multitasking', 'prioritization', 'customer service', 'sales', 'marketing'
        ]
        
        text_lower = text.lower()
        
        found_tech_skills = []
        found_soft_skills = []
        
        # Find technical skills
        for skill in tech_skills:
            if skill in text_lower:
                found_tech_skills.append(skill.title())
        
        # Find soft skills
        for skill in soft_skills:
            if skill in text_lower:
                found_soft_skills.append(skill.title())
        
        return {
            'technical_skills': sorted(found_tech_skills),
            'soft_skills': sorted(found_soft_skills)
        }
    except Exception as e:
        app.logger.error(f"Error extracting skills: {str(e)}")
        return {'technical_skills': [], 'soft_skills': []}

def extract_education(text):
    """Extract education information"""
    try:
        education_patterns = [
            r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|B\.S\.|M\.S\.|B\.A\.|M\.A\.|Ph\.D\.|B\.Tech|M\.Tech)[^.]*\b',
            r'\b(?:University|College|Institute|School)[^.]*\b',
            r'\b(?:Degree|Diploma|Certificate)[^.]*\b',
            r'\b(?:Computer Science|Engineering|Business|Arts|Science)[^.]*\b'
        ]
        
        education_info = []
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 5:  # Filter out very short matches
                    education_info.append(match.strip())
        
        return list(set(education_info))[:10]  # Limit to 10 most relevant items
    except Exception as e:
        app.logger.error(f"Error extracting education: {str(e)}")
        return []

def extract_experience(text):
    """Extract experience information"""
    try:
        experience_patterns = [
            r'\b\d+[\+]?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)\b',
            r'\b(?:Senior|Junior|Lead|Principal|Staff)[^.]*\b',
            r'\b(?:Manager|Director|VP|President|CEO|CTO|CFO)[^.]*\b',
            r'\b(?:Developer|Engineer|Analyst|Consultant)[^.]*\b',
            r'\b(?:Software|Full Stack|Frontend|Backend)[^.]*\b'
        ]
        
        experience_info = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 3:
                    experience_info.append(match.strip())
        
        return list(set(experience_info))[:10]  # Limit to 10 most relevant items
    except Exception as e:
        app.logger.error(f"Error extracting experience: {str(e)}")
        return []

def analyze_resume(text, job_description=None):
    """Analyze resume text and return comprehensive analysis"""
    try:
        if not text or len(text.strip()) < app.config['MIN_RESUME_WORDS']:
            raise ValueError("Resume text is too short or empty")
        
        analysis = {
            'contact_info': extract_contact_info(text),
            'skills': extract_skills(text),
            'education': extract_education(text),
            'experience': extract_experience(text),
            'word_count': len(text.split()),
            'character_count': len(text),
            'analysis_date': datetime.now().isoformat()
        }
        
        # Calculate job match score if job description provided
        if job_description and job_description.strip():
            try:
                vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
                tfidf_matrix = vectorizer.fit_transform([text, job_description])
                similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                analysis['job_match_score'] = round(similarity_score * 100, 2)
            except Exception as e:
                app.logger.warning(f"Could not calculate job match score: {str(e)}")
                analysis['job_match_score'] = 0
        
        return analysis
        
    except Exception as e:
        app.logger.error(f"Error analyzing resume: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    try:
        # Validate file
        file = request.files.get('file')
        is_valid, message = validate_file(file)
        
        if not is_valid:
            return jsonify({'error': message}), 400
        
        job_description = request.form.get('job_description', '').strip()
        
        # Secure filename and save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract text from resume
            file_extension = filename.rsplit('.', 1)[1].lower()
            resume_text, extract_error = safe_file_operation(extract_resume_text, file_path, file_extension)
            
            if extract_error:
                return jsonify({'error': f'Error extracting text: {extract_error}'}), 400
            
            if not resume_text or not resume_text.strip():
                return jsonify({'error': 'Could not extract text from the file'}), 400
            
            # Analyze resume
            analysis = analyze_resume(resume_text, job_description)
            
            # Prepare resume preview
            preview_length = app.config['MAX_RESUME_PREVIEW_CHARS']
            resume_preview = resume_text[:preview_length] + '...' if len(resume_text) > preview_length else resume_text
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except Exception as e:
                app.logger.warning(f"Could not delete uploaded file: {str(e)}")
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'resume_text': resume_preview
            })
            
        except Exception as e:
            # Clean up uploaded file on error
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            
            app.logger.error(f"Resume processing error: {str(e)}")
            return jsonify({'error': f'Error processing resume: {str(e)}'}), 500
    
    except Exception as e:
        app.logger.error(f"Upload endpoint error: {str(e)}")
        return jsonify({'error': 'Server error during file upload'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        app.logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=5000)
