from app import create_app
from models.database import db, User

app = create_app()
with app.app_context():
    users = User.query.all()
    
    print("ALL USERS IN DATABASE:")
    print("=" * 80)
    for user in users:
        print(f"ID: {user.id}")
        print(f"  Name: {user.name}")
        print(f"  Email: {user.email}")
        print(f"  Is Admin: {user.is_admin}")
        print(f"  Plan: {user.plan_type}")
        print(f"  Created: {user.created_at}")
        print("-" * 80)
    
    # Check for any suspicious patterns
    print(f"\nTotal Users: {len(users)}")
    print(f"Admin Users: {len([u for u in users if u.is_admin])}")
    print(f"Non-Admin Users: {len([u for u in users if not u.is_admin])}")
