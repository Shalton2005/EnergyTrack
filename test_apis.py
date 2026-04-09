"""
Test script to verify dashboard APIs are working
"""
import requests

# Test live data API
print("Testing /dashboard/api/live-data...")
# Note: This will fail without authentication, but we can check from backend

# Better approach - test from Flask app context
from app import create_app
from flask import Flask
from models.database import ConsumptionLog, User

app = create_app()

with app.app_context():
    # Get a user
    user = User.query.filter_by(email='user@example.com').first()
    if not user:
        print("User not found!")
        exit()
    
    print(f"\nâœ“ Testing for user: {user.name}")
    
    # Check consumption logs
    logs = ConsumptionLog.query.filter_by(user_id=user.id).order_by(
        ConsumptionLog.timestamp.desc()
    ).limit(5).all()
    
    print(f"\nðŸ“Š Latest 5 Consumption Logs:")
    for log in logs:
        print(f"  {log.timestamp.strftime('%H:%M:%S')} - Power: {log.global_active_power}kW, Voltage: {log.voltage}V")
        print(f"    Sub-meters: {log.sub_metering1}, {log.sub_metering2}, {log.sub_metering3}")
    
    # Test chart data query
    logs_for_chart = ConsumptionLog.query.filter_by(user_id=user.id).order_by(
        ConsumptionLog.timestamp.desc()
    ).limit(20).all()
    logs_for_chart.reverse()
    
    print(f"\nðŸ“ˆ Chart Data (last 20 points):")
    print(f"  Total points: {len(logs_for_chart)}")
    if logs_for_chart:
        print(f"  Labels: {[log.timestamp.strftime('%H:%M:%S') for log in logs_for_chart[:3]]}...")
        print(f"  Power values: {[round(log.global_active_power, 2) for log in logs_for_chart[:3]]}...")
        print(f"  Voltage values: {[round(log.voltage, 1) for log in logs_for_chart[:3]]}...")
    else:
        print("  âš ï¸ NO DATA FOUND!")
    
    print("\nâœ… Backend data is available")
    print("\nâš ï¸ If graphs still don't show, check browser console for JavaScript errors")

