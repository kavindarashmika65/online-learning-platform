from app import db

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.Enum('video', 'document', 'text', name='lesson_types'), nullable=False)
    storage_reference = db.Column(db.String(255), nullable=True)
    text_content = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False)
    is_preview = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'position', name='uq_course_position'),
    )