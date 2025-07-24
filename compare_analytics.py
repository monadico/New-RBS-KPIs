#!/usr/bin/env python3
"""
Analytics Comparison Script
Compares current vs legacy analytics data to identify differences in key metrics.
"""

import json
import os
from datetime import datetime

def load_json_file(file_path):
    """Load JSON file and return data."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return None

def get_latest_period_data(activity_data):
    """Get the latest period data from activity_over_time array."""
    if not activity_data or len(activity_data) == 0:
        return None
    return activity_data[-1]  # Return the last (most recent) period

def compare_analytics():
    """Compare current vs legacy analytics data."""
    print("🔍 Analytics Comparison Report")
    print("=" * 60)
    
    # Load both JSON files
    current_data = load_json_file("new/public/analytics_dump.json")
    legacy_data = load_json_file("jsontest/analytics_dump_legacy.json")
    
    if not current_data or not legacy_data:
        print("❌ Failed to load one or both JSON files")
        return
    
    print(f"📅 Current Analytics Generated: {current_data['metadata']['generated_at']}")
    print(f"📅 Legacy Analytics Generated: {legacy_data['metadata']['generated_at']}")
    print()
    
    # 1. Total Submissions (unique transactions)
    print("1️⃣ TOTAL SUBMISSIONS (Unique Transactions)")
    print("-" * 40)
    current_submissions = current_data['total_metrics']['total_submissions']
    legacy_submissions = legacy_data['total_metrics']['total_submissions']
    submissions_diff = current_submissions - legacy_submissions
    
    print(f"Current:  {current_submissions:,}")
    print(f"Legacy:   {legacy_submissions:,}")
    print(f"Difference: {submissions_diff:+,}")
    print(f"Match: {'✅' if submissions_diff == 0 else '❌'}")
    print()
    
    # 2. Total Active Bettors (unique addresses)
    print("2️⃣ TOTAL ACTIVE BETTORS (Unique Addresses)")
    print("-" * 40)
    current_bettors = current_data['total_metrics']['total_active_addresses']
    legacy_bettors = legacy_data['total_metrics']['total_active_addresses']
    bettors_diff = current_bettors - legacy_bettors
    
    print(f"Current:  {current_bettors:,}")
    print(f"Legacy:   {legacy_bettors:,}")
    print(f"Difference: {bettors_diff:+,}")
    print(f"Match: {'✅' if bettors_diff == 0 else '❌'}")
    print()
    
    # 3. Total MON and JERRY Volume
    print("3️⃣ TOTAL VOLUME")
    print("-" * 40)
    
    # MON Volume
    current_mon = current_data['total_metrics']['total_mon_volume']
    legacy_mon = legacy_data['total_metrics']['total_mon_volume']
    mon_diff = current_mon - legacy_mon
    
    print(f"MON Volume:")
    print(f"  Current:  {current_mon:,.2f}")
    print(f"  Legacy:   {legacy_mon:,.2f}")
    print(f"  Difference: {mon_diff:+,.2f}")
    print(f"  Match: {'✅' if abs(mon_diff) < 0.01 else '❌'}")
    print()
    
    # JERRY Volume
    current_jerry = current_data['total_metrics']['total_jerry_volume']
    legacy_jerry = legacy_data['total_metrics']['total_jerry_volume']
    jerry_diff = current_jerry - legacy_jerry
    
    print(f"JERRY Volume:")
    print(f"  Current:  {current_jerry:,.2f}")
    print(f"  Legacy:   {legacy_jerry:,.2f}")
    print(f"  Difference: {jerry_diff:+,.2f}")
    print(f"  Match: {'✅' if abs(jerry_diff) < 0.01 else '❌'}")
    print()
    
    # 4. Current DAU, WAU, MAU
    print("4️⃣ CURRENT ACTIVE USERS (Latest Period)")
    print("-" * 40)
    
    # DAU (Daily Active Users)
    current_daily = get_latest_period_data(current_data['timeframes']['daily']['activity_over_time'])
    legacy_daily = get_latest_period_data(legacy_data['timeframes']['daily']['activity_over_time'])
    
    if current_daily and legacy_daily:
        current_dau = current_daily['active_addresses']
        legacy_dau = legacy_daily['active_addresses']
        dau_diff = current_dau - legacy_dau
        
        print(f"DAU (Daily Active Users):")
        print(f"  Current:  {current_dau:,}")
        print(f"  Legacy:   {legacy_dau:,}")
        print(f"  Difference: {dau_diff:+,}")
        print(f"  Match: {'✅' if dau_diff == 0 else '❌'}")
        print(f"  Period: {current_daily['start_date']} to {current_daily['end_date']}")
        print()
    
    # WAU (Weekly Active Users)
    current_weekly = get_latest_period_data(current_data['timeframes']['weekly']['activity_over_time'])
    legacy_weekly = get_latest_period_data(legacy_data['timeframes']['weekly']['activity_over_time'])
    
    if current_weekly and legacy_weekly:
        current_wau = current_weekly['active_addresses']
        legacy_wau = legacy_weekly['active_addresses']
        wau_diff = current_wau - legacy_wau
        
        print(f"WAU (Weekly Active Users):")
        print(f"  Current:  {current_wau:,}")
        print(f"  Legacy:   {legacy_wau:,}")
        print(f"  Difference: {wau_diff:+,}")
        print(f"  Match: {'✅' if wau_diff == 0 else '❌'}")
        print(f"  Period: {current_weekly['start_date']} to {current_weekly['end_date']}")
        print()
    
    # MAU (Monthly Active Users)
    current_monthly = get_latest_period_data(current_data['timeframes']['monthly']['activity_over_time'])
    legacy_monthly = get_latest_period_data(legacy_data['timeframes']['monthly']['activity_over_time'])
    
    if current_monthly and legacy_monthly:
        current_mau = current_monthly['active_addresses']
        legacy_mau = legacy_monthly['active_addresses']
        mau_diff = current_mau - legacy_mau
        
        print(f"MAU (Monthly Active Users):")
        print(f"  Current:  {current_mau:,}")
        print(f"  Legacy:   {legacy_mau:,}")
        print(f"  Difference: {mau_diff:+,}")
        print(f"  Match: {'✅' if mau_diff == 0 else '❌'}")
        print(f"  Period: {current_monthly['start_date']} to {current_monthly['end_date']}")
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 60)
    
    total_matches = 0
    total_checks = 0
    
    # Check submissions
    total_checks += 1
    if submissions_diff == 0:
        total_matches += 1
    
    # Check bettors
    total_checks += 1
    if bettors_diff == 0:
        total_matches += 1
    
    # Check MON volume
    total_checks += 1
    if abs(mon_diff) < 0.01:
        total_matches += 1
    
    # Check JERRY volume
    total_checks += 1
    if abs(jerry_diff) < 0.01:
        total_matches += 1
    
    # Check DAU
    if current_daily and legacy_daily:
        total_checks += 1
        if dau_diff == 0:
            total_matches += 1
    
    # Check WAU
    if current_weekly and legacy_weekly:
        total_checks += 1
        if wau_diff == 0:
            total_matches += 1
    
    # Check MAU
    if current_monthly and legacy_monthly:
        total_checks += 1
        if mau_diff == 0:
            total_matches += 1
    
    print(f"✅ Matches: {total_matches}/{total_checks}")
    print(f"❌ Differences: {total_checks - total_matches}/{total_checks}")
    
    if total_matches == total_checks:
        print("🎉 PERFECT MATCH! All metrics are identical.")
    else:
        print("⚠️  Some differences detected. Check the details above.")
    
    print()
    print("🔍 Detailed Analysis Complete!")

if __name__ == "__main__":
    compare_analytics() 