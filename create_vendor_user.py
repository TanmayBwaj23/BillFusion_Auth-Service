#!/usr/bin/env python3
import requests
import json

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "tbj@gmail.com",
    "password": "Pass123!",
    "password_confirm": "Pass123!",
    "first_name": "Test",
    "last_name": "Vendor",
    "role": "vendor",
    "timezone": "UTC",
    "language": "en",
    "terms_accepted": True,
    "marketing_consent": False
}

headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
