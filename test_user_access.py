import requests
import json
import time
import os

def test_user_specific_access():
    base_url = "http://localhost:5000"
    headers = {"Content-Type": "application/json"}
    
    print("\nTesting Security Features:")
    
    # Create test user
    user = {"username": "testuser", "password": "testpass"}
    session = requests.Session()
    
    # Register and login
    session.post(f"{base_url}/signup", headers=headers, json=user)
    session.post(f"{base_url}/login", headers=headers, json=user)
    
    print("\n1. Testing file validation:")
    
    # Test invalid file type
    with open('test.txt', 'w') as f:
        f.write('Test content')
    
    files = {'resume': ('test.txt', open('test.txt', 'rb'), 'text/plain')}
    data = {'job_description': 'Python Developer'}
    response = session.post(f"{base_url}/upload", files=files, data=data)
    print(f"\nUploading invalid file type:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test oversized file
    with open('large.pdf', 'wb') as f:
        f.write(b'0' * (11 * 1024 * 1024))  # 11MB file
    
    files = {'resume': ('large.pdf', open('large.pdf', 'rb'), 'application/pdf')}
    response = session.post(f"{base_url}/upload", files=files, data=data)
    print(f"\nUploading oversized file:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    print("\n2. Testing input validation:")
    
    # Test SQL injection in job description
    files = {'resume': ('test.pdf', open('test.txt', 'rb'), 'application/pdf')}
    data = {'job_description': "Python Developer'; DROP TABLE resumes; --"}
    response = session.post(f"{base_url}/upload", files=files, data=data)
    print(f"\nTesting SQL injection:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test XSS in job description
    data = {'job_description': "<script>alert('XSS')</script>"}
    response = session.post(f"{base_url}/upload", files=files, data=data)
    print(f"\nTesting XSS:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Cleanup
    try:
        os.remove('test.txt')
        os.remove('large.pdf')
    except:
        pass

if __name__ == "__main__":
    print("Testing security features...")
    test_user_specific_access() 