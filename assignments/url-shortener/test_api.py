#!/usr/bin/env python3
"""
Simple test script to verify the URL shortener API functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api():
    print("Testing URL Shortener API...")
    
    # Test health check
    print("\n1. Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test URL shortening
    print("\n2. Testing URL shortening...")
    test_url = "https://www.example.com/very/long/url/with/many/segments"
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={"url": test_url},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    if response.status_code == 201:
        short_code = data["short_code"]
        short_url = data["short_url"]
        
        # Test stats before clicking
        print(f"\n3. Testing stats before clicking...")
        response = requests.get(f"{BASE_URL}/api/stats/{short_code}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test redirect (this will increment clicks)
        print(f"\n4. Testing redirect...")
        response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Location: {response.headers.get('Location', 'None')}")
        
        # Test stats after clicking
        print(f"\n5. Testing stats after clicking...")
        response = requests.get(f"{BASE_URL}/api/stats/{short_code}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    # Test error cases
    print(f"\n6. Testing error cases...")
    
    # Invalid URL
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={"url": "not-a-url"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Invalid URL - Status: {response.status_code}")
    
    # Missing URL
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={},
        headers={"Content-Type": "application/json"}
    )
    print(f"Missing URL - Status: {response.status_code}")
    
    # Non-existent short code
    response = requests.get(f"{BASE_URL}/api/stats/nonexistent")
    print(f"Non-existent short code - Status: {response.status_code}")
    
    print("\nAPI test completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}") 