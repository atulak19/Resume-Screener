import requests
import os

def test_resume_download():
    base_url = "http://localhost:5000"
    headers = {"Content-Type": "application/json"}
    
    print("\nTesting Resume Download Functionality:")
    
    # Test user credentials
    user = {"username": "testuser", "password": "testpass"}
    
    # Create test PDF
    with open('test_resume.pdf', 'wb') as f:
        f.write(b'Test PDF content')
    
    try:
        # Step 1: Register user
        print("\n1. Registering test user...")
        response = requests.post(f"{base_url}/signup", json=user, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Step 2: Login
        print("\n2. Logging in...")
        response = requests.post(f"{base_url}/login", json=user, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Save cookies for session
        cookies = response.cookies
        
        # Step 3: Upload resume
        print("\n3. Uploading test resume...")
        files = {'resume': ('test_resume.pdf', open('test_resume.pdf', 'rb'), 'application/pdf')}
        data = {'job_description': 'Python Developer'}
        response = requests.post(f"{base_url}/upload", files=files, data=data, cookies=cookies)
        print(f"Status Code: {response.status_code}")
        
        # Step 4: Get resume ID
        print("\n4. Getting resume list...")
        response = requests.get(f"{base_url}/api/resumes", cookies=cookies)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        resumes = response.json().get('resumes', [])
        if resumes:
            resume_id = resumes[0]['id']
            
            # Step 5: Download resume
            print(f"\n5. Downloading resume (ID: {resume_id})...")
            response = requests.get(f"{base_url}/api/resumes/{resume_id}/download", cookies=cookies)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Save downloaded file
                with open('downloaded_resume.pdf', 'wb') as f:
                    f.write(response.content)
                print("Resume downloaded successfully!")
                
                # Verify file content
                with open('downloaded_resume.pdf', 'rb') as f:
                    content = f.read()
                print(f"Downloaded file size: {len(content)} bytes")
            
            # Step 6: Test unauthorized access
            print("\n6. Testing unauthorized access...")
            response = requests.get(f"{base_url}/api/resumes/{resume_id}/download")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
        else:
            print("No resumes found!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        
    finally:
        # Cleanup
        try:
            os.remove('test_resume.pdf')
            os.remove('downloaded_resume.pdf')
        except:
            pass

if __name__ == "__main__":
    test_resume_download() 