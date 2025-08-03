from app import app, User, db

with app.app_context():
    users = User.query.all()
    print("Users in database:")
    for user in users:
        print(f"Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
