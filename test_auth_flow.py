import requests
import json
import time

def test_auth_flow(username, password):
    base_url = "http://localhost:5000"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}
    session = requests.Session()  # Use session to maintain cookies
    
    # 1. Signup
    print(f"\nTesting full auth flow with username='{username}', password='{password}'")
    print("\n1. Signup attempt:")
    try:
        response = session.post(f"{base_url}/signup", headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error in signup: {str(e)}")
    
    time.sleep(1)
    
    # 2. Login
    print("\n2. Login attempt:")
    try:
        response = session.post(f"{base_url}/login", headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error in login: {str(e)}")
    
    time.sleep(1)
    
    # 3. Logout
    print("\n3. Logout attempt:")
    try:
        response = session.post(f"{base_url}/logout")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error in logout: {str(e)}")
    
    # 4. Try accessing a protected route after logout (if any)
    print("\n4. Attempting to access protected route after logout:")
    try:
        response = session.get(f"{base_url}/api/resumes")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test with a new user
print("Testing complete authentication flow...")
test_auth_flow("testuser3", "password123") 