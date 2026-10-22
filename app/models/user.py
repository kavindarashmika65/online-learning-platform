from app import db
from flask_login import UserMixin
from datetime import datetime, timezone

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('student', 'teacher', 'admin', name='user_roles'), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    courses = db.relationship('Course', backref='teacher', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    payments = db.relationship('Payment', backref='student', lazy=True)