#!/usr/bin/env python3
"""
Simple test script to validate critical endpoints
Run this after starting the server to check for basic functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_contact_submission():
    """Test contact form submission"""
    url = f"{BASE_URL}/contact/"
    
    # Valid submission
    valid_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "GENERAL",
        "message": "This is a test message that is long enough to pass validation."
    }
    
    print("Testing valid contact submission...")
    try:
        response = requests.post(url, json=valid_data, headers={"Content-Type": "application/json"})
        if response.status_code == 201:
            print("✅ Valid contact submission: PASSED")
        else:
            print(f"❌ Valid contact submission: FAILED - Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Valid contact submission: ERROR - {e}")
    
    # Invalid submission (short message)
    invalid_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "GENERAL",
        "message": "Short"
    }
    
    print("Testing invalid contact submission (short message)...")
    try:
        response = requests.post(url, json=invalid_data, headers={"Content-Type": "application/json"})
        if response.status_code == 400:
            print("✅ Invalid contact submission validation: PASSED")
        else:
            print(f"❌ Invalid contact submission validation: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid contact submission validation: ERROR - {e}")

def test_newsletter_subscription():
    """Test newsletter subscription"""
    subscribe_url = f"{BASE_URL}/newsletter/subscribe/"
    
    # Valid subscription
    valid_data = {"email": "newsletter@example.com"}
    
    print("Testing newsletter subscription...")
    try:
        response = requests.post(subscribe_url, json=valid_data, headers={"Content-Type": "application/json"})
        if response.status_code in [201, 409]:  # 201 for new, 409 for existing
            print("✅ Newsletter subscription: PASSED")
        else:
            print(f"❌ Newsletter subscription: FAILED - Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Newsletter subscription: ERROR - {e}")
    
    # Invalid email
    invalid_data = {"email": "invalid-email"}
    
    print("Testing invalid newsletter subscription...")
    try:
        response = requests.post(subscribe_url, json=invalid_data, headers={"Content-Type": "application/json"})
        if response.status_code == 400:
            print("✅ Invalid newsletter subscription validation: PASSED")
        else:
            print(f"❌ Invalid newsletter subscription validation: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid newsletter subscription validation: ERROR - {e}")

def test_get_contact_subjects():
    """Test getting contact subjects"""
    url = f"{BASE_URL}/contact/subjects/"
    
    print("Testing get contact subjects...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and isinstance(data.get('data'), list):
                print("✅ Get contact subjects: PASSED")
            else:
                print("❌ Get contact subjects: FAILED - Invalid response format")
        else:
            print(f"❌ Get contact subjects: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Get contact subjects: ERROR - {e}")

def main():
    print("🧪 Testing TYMA Backend APIs...")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/contact/subjects/", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first with:")
        print("   python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        sys.exit(1)
    
    test_contact_submission()
    print("-" * 30)
    test_newsletter_subscription()
    print("-" * 30)
    test_get_contact_subjects()
    
    print("=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()
