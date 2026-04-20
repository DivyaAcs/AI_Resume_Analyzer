# AI Resume Analyzer

A comprehensive web application that analyzes resumes using AI and machine learning techniques. Upload your resume to get instant insights about skills, experience, education, and job compatibility.

## Features

- **Multi-format Support**: Accepts PDF, DOCX, and TXT files
- **AI-Powered Analysis**: Extracts and analyzes key information from resumes
- **Job Matching**: Compare resumes against job descriptions for compatibility scoring
- **Skill Detection**: Identifies technical and soft skills
- **Contact Information Extraction**: Automatically finds emails and phone numbers
- **Modern UI**: Responsive, user-friendly interface with drag-and-drop support
- **Real-time Processing**: Fast analysis with visual feedback

## Architecture

```
User → Web UI → Flask Backend → AI Analysis → Results Display
```

### Components

1. **Frontend**: Modern HTML5/CSS3/JavaScript with Bootstrap
2. **Backend**: Flask web server with Python
3. **AI Model**: Scikit-learn based text analysis and similarity scoring
4. **File Processing**: PyPDF2 and python-docx for document parsing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create uploads directory** (the app will create this automatically):
   ```bash
   mkdir uploads
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your web browser and go to `http://localhost:5000`

## Usage

### Basic Resume Analysis

1. Open the web application in your browser
2. Drag and drop a resume file (PDF, DOCX, or TXT) or click to browse
3. Optionally, paste a job description for compatibility scoring
4. Click "Analyze Resume" to process the file
5. View the comprehensive analysis results

### Analysis Results Include

- **Contact Information**: Extracted emails and phone numbers
- **Skills Detection**: 
  - Technical skills (programming languages, frameworks, tools)
  - Soft skills (communication, leadership, etc.)
- **Education Information**: Degrees, institutions, certifications
- **Experience Details**: Years of experience, job titles, responsibilities
- **Job Match Score**: Percentage compatibility with provided job description
- **Resume Statistics**: Word count, character count
- **Resume Preview**: First 500 characters of extracted text

## API Endpoints

### `POST /upload`
Upload and analyze a resume file.

**Request:**
- `file`: Resume file (PDF, DOCX, or TXT)
- `job_description`: Optional job description for matching

**Response:**
```json
{
  "success": true,
  "analysis": {
    "contact_info": {
      "emails": ["email@example.com"],
      "phones": ["+1234567890"]
    },
    "skills": {
      "technical_skills": ["Python", "JavaScript"],
      "soft_skills": ["Leadership", "Communication"]
    },
    "education": ["Bachelor of Science in Computer Science"],
    "experience": ["5+ years of experience"],
    "word_count": 500,
    "character_count": 2500,
    "job_match_score": 85.5
  },
  "resume_text": "First 500 characters..."
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-01T12:00:00"
}
```

## File Upload Limits

- **Maximum file size**: 16MB
- **Supported formats**: PDF, DOCX, TXT
- **Files are automatically deleted** after processing

## Technology Stack

- **Backend**: Flask 2.3.3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: Scikit-learn 1.3.0
- **Document Processing**: PyPDF2, python-docx
- **Data Processing**: NumPy, Pandas

## Development

### Project Structure

```
AI project 1/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/
│   └── index.html        # Main web interface
└── uploads/              # Temporary file storage (auto-created)
```

### Customization

To add new skills to detect, modify the `tech_skills` and `soft_skills` lists in the `extract_skills()` function in `app.py`.

To improve the job matching algorithm, you can:
- Add more sophisticated text preprocessing
- Use advanced NLP techniques
- Implement custom weighting for different skills
- Add industry-specific keywords

## Deployment

### Production Deployment

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t resume-analyzer .
docker run -p 5000:5000 resume-analyzer
```

## Security Considerations

- File uploads are validated for type and size
- Uploaded files are automatically deleted after processing
- Input sanitization is implemented
- No sensitive data is stored permanently

## Troubleshooting

### Common Issues

1. **"Could not extract text from file"**: Ensure the file is not corrupted and is a valid PDF/DOCX/TXT file
2. **"File type not allowed"**: Only PDF, DOCX, and TXT files are supported
3. **"File too large"**: Maximum file size is 16MB
4. **Port already in use**: Change the port in `app.py` or stop the conflicting service

### Logs

Check the console output for detailed error messages. The application runs in debug mode by default.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the project repository.
