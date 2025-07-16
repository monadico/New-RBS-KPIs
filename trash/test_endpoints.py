#!/usr/bin/env python3
"""
Test script for API endpoints
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, name):
    """Test an endpoint and measure response time."""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing {name} ({endpoint})...")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ {name} - SUCCESS ({end_time - start_time:.2f}s)")
                response_data = data.get('data', {})
                if isinstance(response_data, dict):
                    print(f"   Response keys: {list(response_data.keys())}")
                elif isinstance(response_data, list):
                    print(f"   Items returned: {len(response_data)}")
                    if response_data and isinstance(response_data[0], dict):
                        print(f"   First item keys: {list(response_data[0].keys())}")
                return True
            else:
                print(f"❌ {name} - FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ {name} - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ {name} - TIMEOUT (>30s)")
        return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {str(e)}")
        return False

def main():
    """Test all endpoints."""
    print("🚀 Testing API Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/stats", "Basic Stats"),
        ("/api/totals", "Total Stats"),
        ("/api/daily", "Daily Metrics"),
        ("/api/periods", "Period Stats"),
        ("/api/heatmap", "Heatmap Data"),
        ("/api/token-volumes", "Token Volumes"),
        ("/api/retention", "User Retention"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        success = test_endpoint(endpoint, name)
        results.append((name, success))
    
    print("\n📊 Summary:")
    print("=" * 50)
    working = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 Overall: {working}/{total} endpoints working")

if __name__ == "__main__":
    main() 