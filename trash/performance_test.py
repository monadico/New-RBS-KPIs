#!/usr/bin/env python3
"""
Performance Test Script
=======================

This script demonstrates the benefits of our optimized analytics approach:
1. Single JSON with all timeframes
2. Compression for faster loading
3. Organized structure for easy access
"""

import json
import gzip
import time
import os

def test_file_sizes():
    """Test file sizes and compression ratios."""
    files = [
        "frontend2/public/analytics_dump.json",
        "frontend2/public/analytics_dump.json.gz"
    ]
    
    print("📊 File Size Analysis:")
    print("=" * 50)
    
    for file_path in files:
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"📁 {file_path}: {size_kb:.1f} KB")
        else:
            print(f"❌ {file_path}: Not found")

def test_json_structure():
    """Test the new JSON structure."""
    try:
        with open("frontend2/public/analytics_dump.json", "r") as f:
            data = json.load(f)
        
        print("\n🔍 JSON Structure Analysis:")
        print("=" * 50)
        
        # Check if new structure exists
        if "timeframes" in data:
            print("✅ New optimized structure found")
            timeframes = list(data["timeframes"].keys())
            print(f"📅 Available timeframes: {', '.join(timeframes)}")
            
            # Check data sizes
            for timeframe in timeframes:
                activity_data = data["timeframes"][timeframe]["activity_over_time"]
                card_data = data["timeframes"][timeframe]["slips_by_card_count"]
                print(f"   {timeframe}: {len(activity_data)} periods, {len(card_data)} card count entries")
        else:
            print("⚠️  Using legacy structure")
            
        # Check metadata
        if "metadata" in data:
            print(f"📋 Metadata: {data['metadata']}")
            
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")

def simulate_frontend_loading():
    """Simulate frontend loading performance."""
    print("\n⚡ Frontend Loading Simulation:")
    print("=" * 50)
    
    # Test uncompressed loading
    start_time = time.time()
    try:
        with open("frontend2/public/analytics_dump.json", "r") as f:
            data = json.load(f)
        uncompressed_time = time.time() - start_time
        print(f"📄 Uncompressed loading: {uncompressed_time:.3f}s")
    except:
        print("❌ Could not test uncompressed loading")
    
    # Test compressed loading
    start_time = time.time()
    try:
        with gzip.open("frontend2/public/analytics_dump.json.gz", "rt") as f:
            data = json.load(f)
        compressed_time = time.time() - start_time
        print(f"🗜️  Compressed loading: {compressed_time:.3f}s")
        
        if 'uncompressed_time' in locals():
            speedup = uncompressed_time / compressed_time
            print(f"🚀 Speedup: {speedup:.1f}x faster")
            
    except:
        print("❌ Could not test compressed loading")

def main():
    """Run all performance tests."""
    print("🧪 Analytics Performance Test")
    print("=" * 60)
    
    test_file_sizes()
    test_json_structure()
    simulate_frontend_loading()
    
    print("\n✅ Performance test completed!")

if __name__ == "__main__":
    main() 