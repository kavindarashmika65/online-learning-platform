from app import db
from datetime import datetime, timezone

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='LKR', nullable=False)
    status = db.Column(db.Enum('pending', 'succeeded', 'failed', 'cancelled', 'refunded', name='payment_status'), nullable=False, index=True)
    gateway_name = db.Column(db.String(50), nullable=False)
    gateway_transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)