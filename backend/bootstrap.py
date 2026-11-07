"""First-run setup. Safe to run on every start: it never drops or overwrites data.

- Creates the three roles (Admin, Manager, Operator) if missing.
- Creates the first Admin only when the database has no users yet, from ADMIN_USERNAME,
  ADMIN_EMAIL and ADMIN_PASSWORD. The Admin must change that password at first login.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models.user import User, UserType

ROLES = [(1, "Admin"), (2, "Manager"), (3, "Operator")]


def bootstrap():
    app = create_app(os.getenv('FLASK_CONFIG', 'production'))
    with app.app_context():
        for role_id, name in ROLES:
            if not db.session.get(UserType, role_id):
                db.session.add(UserType(id=role_id, name=name))
        db.session.commit()

        if User.query.count() > 0:
            return
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')
        if not username or not password or len(password) < 8:
            print("No users yet. Set ADMIN_USERNAME and ADMIN_PASSWORD (8+ chars) to create the first Admin.")
            return
        admin = User(username=username, email=os.getenv('ADMIN_EMAIL', f'{username}@example.com'),
                     user_type_id=1, must_change_password=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Created first Admin '{username}'. Change the password at first login.")


if __name__ == '__main__':
    bootstrap()
