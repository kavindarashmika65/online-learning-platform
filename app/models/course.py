from app import db
from datetime import datetime, timezone

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    courses = db.relationship('Course', backref='category', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    thumbnail_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('draft', 'pending', 'published', 'rejected', 'archived', name='course_status'), nullable=False, index=True)
    rejection_reason = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    lessons = db.relationship('Lesson', backref='course', cascade="all, delete-orphan", lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    reviews = db.relationship('Review', backref='course', lazy=True)
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='courses_taught') # මෙය අලුතින් එක් කරන්න
    lessons = db.relationship('Lesson', backref='course', cascade="all, delete-orphan", lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    reviews = db.relationship('Review', backref='course', lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='uq_student_course_review'),)