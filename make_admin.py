from app import app, User, db

with app.app_context():
    user = User.query.filter_by(username='test').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"User {user.username} is now an admin.")
    else:
        print("User 'test' not found.")
