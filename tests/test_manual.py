# Manual Test Script for LLM Code Deployment API

import requests
import json
import base64
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
TEST_SECRET = "dev-secret-123"  # Update this to match your .env

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("🔍 Testing root endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_api_endpoint_build():
    """Test the main API endpoint with a build request"""
    print("🔍 Testing API endpoint (Build Phase)...")
    
    # Create test request
    request_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": f"test-{int(time.time())}",  # Unique task ID
        "round": 1,
        "nonce": f"nonce-{int(time.time())}",
        "brief": """Create a simple todo list application with the following features:
        - Add new tasks with an input field and button
        - Display tasks in a list
        - Mark tasks as complete/incomplete
        - Delete tasks
        - Show total task count
        - Use Bootstrap 5 for styling
        - Make it responsive for mobile devices""",
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "checks": [
            "Must have #add-task button",
            "Must have #task-input field",
            "Must display #task-count",
            "Must have task list container"
        ],
        "attachments": [
            {
                "filename": "sample-data.json",
                "content": base64.b64encode(json.dumps({
                    "sample_tasks": [
                        {"id": 1, "text": "Learn HTML", "completed": False},
                        {"id": 2, "text": "Build a website", "completed": False},
                        {"id": 3, "text": "Deploy to GitHub", "completed": True}
                    ]
                }).encode()).decode()
            }
        ]
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            f"{API_BASE_URL}/api",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Build request accepted successfully!")
            print("⏳ Deployment is processing in the background...")
            print("📧 Check the evaluation endpoint for results")
            return True
        else:
            print(f"❌ Build request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_api_endpoint_invalid_data():
    """Test the API endpoint with invalid data"""
    print("🔍 Testing API endpoint with invalid data...")
    
    test_cases = [
        # Missing required fields
        {
            "name": "Missing email",
            "data": {"secret": TEST_SECRET, "task": "test"},
            "expected_status": 400
        },
        # Invalid secret
        {
            "name": "Invalid secret",
            "data": {
                "email": "test@example.com",
                "secret": "invalid-secret",
                "task": "test",
                "round": 1,
                "nonce": "test",
                "brief": "test",
                "evaluation_url": "https://example.com"
            },
            "expected_status": 401
        },
        # Invalid round
        {
            "name": "Invalid round",
            "data": {
                "email": "test@example.com",
                "secret": TEST_SECRET,
                "task": "test",
                "round": 3,  # Invalid
                "nonce": "test",
                "brief": "test",
                "evaluation_url": "https://example.com"
            },
            "expected_status": 400
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"  Testing: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == test_case["expected_status"]:
                print(f"    ✅ Correctly returned {response.status_code}")
            else:
                print(f"    ❌ Expected {test_case['expected_status']}, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"    ❌ Test failed: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all manual tests"""
    print("🚀 Starting Manual Tests for LLM Code Deployment API")
    print(f"📍 API Base URL: {API_BASE_URL}")
    print(f"🔑 Test Secret: {TEST_SECRET}")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Invalid Data Handling", test_api_endpoint_invalid_data),
        ("Build Request", test_api_endpoint_build),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🏆 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Next Steps:")
    print("1. Make sure the API server is running (python app.py)")
    print("2. Check your .env configuration")
    print("3. Verify GitHub CLI is installed and authenticated")
    print("4. Check OpenAI API key is valid")

if __name__ == "__main__":
    main()