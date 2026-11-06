from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # ඔබේ Account එක සෑදූ Email එක මෙතැනට දෙන්න
    user = User.query.filter_by(email='admin@gmail.com').first()
    if user:
        user.role = 'admin'
        db.session.commit()
        print("Successfully promoted to Admin!")
    else:
        print("User not found!")