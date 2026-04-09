import os

from app import create_app
from models.database import db, User

app = create_app()
with app.app_context():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@energytrack.local')

    # Find all admin users
    admins = User.query.filter_by(is_admin=True).all()
    
    print(f"Found {len(admins)} admin users:")
    for admin in admins:
        print(f"  - ID: {admin.id}, Email: {admin.email}, Name: {admin.name}")
    
    # Keep only configured admin email as admin, remove admin flag from others
    if len(admins) > 1:
        print("\nFixing duplicate admins...")
        for admin in admins:
            if admin.email != admin_email:
                print(f"  Removing admin privileges from: {admin.email}")
                admin.is_admin = False
        
        db.session.commit()
        print("✓ Fixed duplicate admin accounts")
    
    # Set admin plan to None (no plan needed)
    main_admin = User.query.filter_by(email=admin_email).first()
    if main_admin:
        print(f"\nUpdating admin account settings...")
        main_admin.plan_type = None
        main_admin.trial_ends_at = None
        main_admin.subscription_started_at = None
        db.session.commit()
        print("✓ Admin account updated (no plan required)")
    
    print("\n✓ All fixes complete!")
