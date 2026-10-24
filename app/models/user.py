from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('student', 'teacher', 'admin', name='user_roles'), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # ගුරුවරුන්ගේ බැංකු විස්තර සඳහා (Bank Details for Teachers)
    bank_name = db.Column(db.String(100), nullable=True)
    account_name = db.Column(db.String(100), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    branch = db.Column(db.String(100), nullable=True)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    reviews = db.relationship('Review', backref='student', lazy=True)
    # Note: Course relationship is handled in Course model via backref

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)