from flask import render_template, redirect, url_for, flash, abort, request
from app.student import student_bp
from flask_login import login_required, current_user
from app import db
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        abort(403)
    # ශිෂ්‍යයා දැනට ලබාගෙන ඇති Active Courses ලබාගැනීම
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('student/dashboard.html', enrollments=enrollments)

@student_bp.route('/browse-courses')
@login_required
def browse_courses():
    if current_user.role != 'student':
        abort(403)
    # ගුරුවරුන් Publish කර ඇති සියලුම පාඨමාලා ලබාගැනීම
    courses = Course.query.filter_by(status='published').all()
    # දැනටමත් මිලදී ගෙන ඇති පාඨමාලා වල ID වෙන් කරගැනීම
    enrolled_course_ids = [e.course_id for e in Enrollment.query.filter_by(student_id=current_user.id).all()]
    return render_template('student/browse_courses.html', courses=courses, enrolled_course_ids=enrolled_course_ids)

@student_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    if current_user.role != 'student':
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    existing_enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
    else:
        new_enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
        db.session.add(new_enrollment)
        db.session.commit()
        flash(f'Successfully enrolled in {course.title}!', 'success')
        
    return redirect(url_for('student.dashboard'))

@student_bp.route('/remove-course/<int:course_id>', methods=['POST'])
@login_required
def remove_course(course_id):
    if current_user.role != 'student':
        abort(403)
    
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first_or_404()
    db.session.delete(enrollment)
    db.session.commit()
    flash('Course removed from your active list.', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/learn/<int:course_id>')
@login_required
def learn(course_id):
    if current_user.role != 'student':
        abort(403)
    
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first_or_404()
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.position).all()
    return render_template('student/learn.html', course=enrollment.course, lessons=lessons)

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        abort(403)
        
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))
        
    return render_template('student/profile.html')