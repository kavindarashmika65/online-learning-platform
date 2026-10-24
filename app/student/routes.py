from flask import render_template, redirect, url_for, flash, abort, request
from app.student import student_bp
from flask_login import login_required, current_user
from app import db
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
import os
import uuid
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, abort, request


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

@student_bp.route('/checkout/<int:course_id>', methods=['GET', 'POST'])
@login_required
def checkout(course_id):
    if current_user.role != 'student':
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    existing_enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    
    # දැනටමත් Enroll වී ඇත්නම් හෝ Pending නම්
    if existing_enrollment:
        if existing_enrollment.status == 'pending':
            flash('Your payment is currently being reviewed by the teacher.', 'info')
        else:
            flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        if 'receipt' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(request.url)
            
        file = request.files['receipt']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)
            
        if file:
            # ගොනුවේ නම ආරක්ෂිතව වෙනස් කිරීම (Unique name)
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
            
            # Receipts ගබඩා කරන Folder එක සෑදීම
            upload_folder = os.path.join('app', 'static', 'uploads', 'receipts')
            os.makedirs(upload_folder, exist_ok=True)
            
            # ගොනුව Save කිරීම
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Pending තත්ත්වයෙන් Enrollment එකක් සෑදීම
            new_enrollment = Enrollment(
                student_id=current_user.id, 
                course_id=course.id,
                status='pending',
                receipt_path=filename
            )
            db.session.add(new_enrollment)
            db.session.commit()
            
            flash('Payment receipt uploaded successfully! Please wait for the teacher to approve.', 'success')
            return redirect(url_for('student.dashboard'))
            
    return render_template('student/checkout.html', course=course)

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
        
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    
    # Approve වී නොමැති නම් පන්තියට යාම සම්පූර්ණයෙන්ම අවහිර කිරීම
    if not enrollment:
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    if enrollment.status == 'pending':
        flash('Your payment is still pending. Please wait for the teacher to approve.', 'warning')
        return redirect(url_for('student.dashboard'))
        
    if enrollment.status == 'rejected':
        flash('Your payment was rejected. Please contact the teacher.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    # Status එක 'approved' නම් පමණක් පාඩම් බැලීමට ඉඩදීම
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.position).all()
    return render_template('student/learn.html', course=course, lessons=lessons)

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