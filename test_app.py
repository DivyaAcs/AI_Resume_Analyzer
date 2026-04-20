#!/usr/bin/env python3
"""
Test script for AI Resume Analyzer
"""

import requests
import json
import os
import sys
from datetime import datetime

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("PASS: Health check passed")
            return True
        else:
            print(f"FAIL: Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("FAIL: Could not connect to server. Make sure the app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"FAIL: Health check error: {str(e)}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    # Create a test resume file
    test_resume_content = """
    John Doe
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology
    
    EXPERIENCE
    Senior Software Engineer - 5+ years of experience
    - Developed web applications using Python, JavaScript, React
    - Worked with AWS, Docker, and Kubernetes
    - Led a team of 5 developers
    
    SKILLS
    Technical: Python, JavaScript, React, Node.js, AWS, Docker
    Soft: Leadership, Communication, Problem Solving
    """
    
    # Save test file
    test_file_path = "test_resume.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_resume_content)
    
    try:
        # Test file upload
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'job_description': 'Looking for a Senior Software Engineer with Python and React experience'}
            
            response = requests.post('http://localhost:5000/upload', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("PASS: File upload test passed")
                    
                    # Check analysis results
                    analysis = result.get('analysis', {})
                    
                    # Check contact info
                    contact_info = analysis.get('contact_info', {})
                    if contact_info.get('emails'):
                        print(f"PASS: Email detected: {contact_info['emails'][0]}")
                    else:
                        print("WARN: No email detected")
                    
                    if contact_info.get('phones'):
                        print(f"PASS: Phone detected: {contact_info['phones'][0]}")
                    else:
                        print("WARN: No phone detected")
                    
                    # Check skills
                    skills = analysis.get('skills', {})
                    tech_skills = skills.get('technical_skills', [])
                    soft_skills = skills.get('soft_skills', [])
                    
                    if tech_skills:
                        print(f"PASS: Technical skills detected: {', '.join(tech_skills[:3])}...")
                    else:
                        print("WARN: No technical skills detected")
                    
                    if soft_skills:
                        print(f"PASS: Soft skills detected: {', '.join(soft_skills[:3])}...")
                    else:
                        print("WARN: No soft skills detected")
                    
                    # Check job match score
                    if 'job_match_score' in analysis:
                        print(f"PASS: Job match score: {analysis['job_match_score']}%")
                    else:
                        print("WARN: No job match score calculated")
                    
                    return True
                else:
                    print(f"FAIL: Upload failed: {result.get('error')}")
                    return False
            else:
                print(f"FAIL: Upload request failed: {response.status_code}")
                try:
                    error_info = response.json()
                    print(f"Error: {error_info.get('error')}")
                except:
                    print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"FAIL: File upload test error: {str(e)}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_invalid_file():
    """Test invalid file handling"""
    try:
        # Test with invalid file type
        files = {'file': ('test.jpg', b'fake image content', 'image/jpeg')}
        response = requests.post('http://localhost:5000/upload', files=files)
        
        if response.status_code == 400:
            print("PASS: Invalid file type test passed")
            return True
        else:
            print(f"FAIL: Invalid file type test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAIL: Invalid file test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Testing AI Resume Analyzer...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("File Upload", test_file_upload),
        ("Invalid File", test_invalid_file)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} Test...")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The application is working correctly.")
        return 0
    else:
        print("Some tests failed. Please check the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
