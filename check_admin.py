import os

from app import create_app
from models.database import db, User

app = create_app()
with app.app_context():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@energytrack.local')
    check_password = os.getenv('ADMIN_PASSWORD', '')
    admin = User.query.filter_by(email=admin_email).first()
    
    if admin:
        print(f"✓ Admin user found")
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.name}")
        print(f"  Is Admin: {admin.is_admin}")
        if check_password:
            print(f"  Password check (from ADMIN_PASSWORD): {admin.check_password(check_password)}")
        else:
            print("  Password check skipped (set ADMIN_PASSWORD to enable check)")
    else:
        print("✗ Admin user NOT found in database")
        print("\nAll users in database:")
        users = User.query.all()
        for u in users:
            print(f"  - {u.email} (admin: {u.is_admin})")
