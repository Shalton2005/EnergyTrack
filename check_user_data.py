import os

from app import create_app
from models.database import db, ConsumptionLog, User

app = create_app()
with app.app_context():
    target_email = os.getenv('CHECK_USER_EMAIL', '')
    if not target_email:
        print('Set CHECK_USER_EMAIL to inspect a specific user.')
        raise SystemExit(1)

    user = User.query.filter_by(email=target_email).first()
    if user:
        logs = ConsumptionLog.query.filter_by(user_id=user.id).count()
        print(f'✓ User: {user.name}')
        print(f'  Total consumption logs: {logs}')
        
        if logs > 0:
            recent = ConsumptionLog.query.filter_by(user_id=user.id).order_by(ConsumptionLog.timestamp.desc()).first()
            print(f'  Latest reading: {recent.timestamp}')
            print(f'  Power: {recent.global_active_power} kW')
            print(f'  Voltage: {recent.voltage} V')
        else:
            print('  ⚠️ NO DATA - User needs to visit dashboard to start simulation')
    else:
        print(f'✗ User not found: {target_email}')
