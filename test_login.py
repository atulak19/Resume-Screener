import requests
import json

def test_login(username, password):
    url = "http://localhost:5000/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"\nTest with username='{username}', password='{password}':")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test cases
print("Testing Login API...")
test_login("newuser", "testpass123")  # Correct credentials
test_login("newuser", "wrongpass")    # Wrong password
test_login("", "")                    # Empty credentials 