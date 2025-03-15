import requests
import json
import time

def test_signup_and_login(username, password):
    base_url = "http://localhost:5000"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}
    
    # First, try to signup
    print(f"\nTesting with username='{username}', password='{password}'")
    print("\n1. Signup attempt:")
    try:
        response = requests.post(f"{base_url}/signup", headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Wait a bit before trying to login
    time.sleep(1)
    
    # Then, try to login
    print("\n2. Login attempt:")
    try:
        response = requests.post(f"{base_url}/login", headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test with a new user
print("Testing Signup and Login flow...")
test_signup_and_login("testuser2", "password123") 