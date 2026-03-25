import requests
import json

url = "http://127.0.0.1:8000/api/auth/login"
data = {
    "email": "test@example.com",
    "password": "Password123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
