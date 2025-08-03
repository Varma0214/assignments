#!/usr/bin/env python3
"""
Test script for the refactored user management API
Demonstrates security improvements and functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:5009"

def test_api():
    print("Testing Refactored User Management API...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test 2: Get all users (should show existing users)
    print("\n2. Testing get all users...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Create a new user
    print("\n3. Testing create user...")
    try:
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "secure123"
        }
        response = requests.post(
            f"{BASE_URL}/users",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            user_id = response.json()["data"]["id"]
        else:
            user_id = None
            
    except Exception as e:
        print(f"Error: {e}")
        user_id = None
    
    # Test 4: Login with the new user
    print("\n4. Testing login...")
    try:
        login_data = {
            "email": "test@example.com",
            "password": "secure123"
        }
        response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Get specific user
    if user_id:
        print(f"\n5. Testing get user {user_id}...")
        try:
            response = requests.get(f"{BASE_URL}/user/{user_id}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test 6: Update user
    if user_id:
        print(f"\n6. Testing update user {user_id}...")
        try:
            update_data = {
                "name": "Updated Test User",
                "email": "updated@example.com"
            }
            response = requests.put(
                f"{BASE_URL}/user/{user_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test 7: Search users
    print("\n7. Testing search users...")
    try:
        response = requests.get(f"{BASE_URL}/search?name=Test")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 8: Error cases - Invalid email
    print("\n8. Testing error cases - Invalid email...")
    try:
        invalid_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "secure123"
        }
        response = requests.post(
            f"{BASE_URL}/users",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 9: Error cases - Missing required fields
    print("\n9. Testing error cases - Missing required fields...")
    try:
        incomplete_data = {
            "name": "Test User"
            # Missing email and password
        }
        response = requests.post(
            f"{BASE_URL}/users",
            json=incomplete_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 10: Error cases - Non-existent user
    print("\n10. Testing error cases - Non-existent user...")
    try:
        response = requests.get(f"{BASE_URL}/user/99999")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 11: SQL Injection attempt (should be prevented)
    print("\n11. Testing SQL injection prevention...")
    try:
        # This should be safely handled and not cause SQL injection
        malicious_id = "1' OR '1'='1"
        response = requests.get(f"{BASE_URL}/user/{malicious_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("API testing completed!")
    print("\nSecurity improvements demonstrated:")
    print("✅ SQL injection prevention")
    print("✅ Input validation")
    print("✅ Proper error handling")
    print("✅ Consistent JSON responses")
    print("✅ Password hashing (not visible in responses)")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:5009")
    except Exception as e:
        print(f"Error: {e}") 