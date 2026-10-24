from app import db
from datetime import datetime, timezone

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # ගෙවීම් විස්තර (Payment Tracking)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='payment_status'), default='pending', nullable=False)
    receipt_path = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uq_student_course_enrollment'),
    )