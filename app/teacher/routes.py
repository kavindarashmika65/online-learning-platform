import os
import re
from datetime import datetime
from flask import render_template, redirect, url_for, flash, abort, current_app
from app.teacher import teacher_bp
from app.teacher.forms import CourseForm, LessonForm
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, Category
from app.models.lesson import Lesson
from werkzeug.utils import secure_filename
from app.teacher.forms import BankDetailsForm
from flask import request
from app.models.enrollment import Enrollment

def generate_slug(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'[-\s]+', '-', slug).strip('-') + f"-{int(datetime.utcnow().timestamp())}"

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        abort(403)
        
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    course_ids = [c.id for c in courses] if courses else []
    
    # Approved වූ සිසුන්ගේ දත්ත පමණක් ගණනය කිරීම
    approved_enrollments = Enrollment.query.filter(
        Enrollment.course_id.in_(course_ids),
        Enrollment.status == 'approved'
    ).all() if course_ids else []
    
    total_courses = len(courses)
    total_students = len(set(e.student_id for e in approved_enrollments))
    total_earnings = sum(e.course.price for e in approved_enrollments)
    
    # Approve කිරීම සඳහා Pending ඇති ලැයිස්තුව ලබාගැනීම
    pending_requests = Enrollment.query.filter(
        Enrollment.course_id.in_(course_ids),
        Enrollment.status == 'pending'
    ).all() if course_ids else []
    
    return render_template('teacher/dashboard.html',
                           total_courses=total_courses,
                           total_students=total_students,
                           total_earnings=total_earnings,
                           pending_requests=pending_requests)

# Approve හෝ Reject කිරීමේ කේතය (ගොනුවේ අවසානයටම එක් කරන්න)
# Approve හෝ Reject කිරීමේ කේතය
@teacher_bp.route('/enrollment/<int:enrollment_id>/<action>', methods=['POST'])
@login_required
def handle_enrollment(enrollment_id, action):
    if current_user.role != 'teacher':
        abort(403)
        
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.course.teacher_id != current_user.id:
        abort(403)
        
    if action == 'approve':
        enrollment.status = 'approved'
        flash(f'Payment approved for {enrollment.student.full_name}. They can now access the course.', 'success')
    elif action == 'reject':
        enrollment.status = 'rejected'
        flash('Payment rejected.', 'danger')
        
    db.session.commit()
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/create-course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'teacher':
        
         abort(403)
        
    form = CourseForm()
    if form.validate_on_submit():
        category = Category.query.first()
        if not category:
            category = Category(name="General", slug="general")
            db.session.add(category)
            db.session.commit()

        course = Course(
            title=form.title.data,
            slug=generate_slug(form.title.data),
            description=form.description.data,
            price=form.price.data,
            teacher_id=current_user.id,
            category_id=category.id,
            status='published'
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('teacher.dashboard'))
        
    return render_template('teacher/create_course.html', form=form)

@teacher_bp.route('/course/<int:course_id>/lessons', methods=['GET', 'POST'])
@login_required
def manage_lessons(course_id):
    if current_user.role != 'teacher':
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        abort(403)

    form = LessonForm()
    if form.validate_on_submit():
        if not form.video_url.data and not form.pdf_file.data:
            flash('Please provide either a Video URL or a PDF file.', 'warning')
            return redirect(url_for('teacher.manage_lessons', course_id=course.id))

        # ඊළඟ පාඩම් අංකය (position) සොයාගැනීම
        last_lesson = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.position.desc()).first()
        next_position = (last_lesson.position + 1) if last_lesson else 1

        # 1. Video එකක් ලබා දී ඇත්නම් එය සෑදීම
        if form.video_url.data:
            lesson_vid = Lesson(
                title=form.title.data if not form.pdf_file.data else f"{form.title.data} (Video)",
                content_type='video',
                storage_reference=form.video_url.data,
                position=next_position,
                course_id=course.id
            )
            db.session.add(lesson_vid)
            next_position += 1

        # 2. PDF ගොනුවක් ලබා දී ඇත්නම් එය සෑදීම
        if form.pdf_file.data:
            file = form.pdf_file.data
            pdf_filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.root_path, 'static/uploads/pdfs')
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, pdf_filename))

            lesson_pdf = Lesson(
                title=form.title.data if not form.video_url.data else f"{form.title.data} (PDF)",
                content_type='document',
                storage_reference=pdf_filename,
                position=next_position,
                course_id=course.id
            )
            db.session.add(lesson_pdf)

        db.session.commit()
        flash('Lesson(s) added successfully!', 'success')
        return redirect(url_for('teacher.manage_lessons', course_id=course.id))

    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.position).all()
    return render_template('teacher/manage_lessons.html', course=course, form=form, lessons=lessons)

@teacher_bp.route('/my-courses')
@login_required
def my_courses():
    if current_user.role != 'teacher':
        abort(403)
    # අලුත්ම පාඨමාලා මුලින් එන සේ ලබා ගැනීම
    courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.created_at.desc()).all()
    return render_template('teacher/my_courses.html', courses=courses)

@teacher_bp.route('/edit-course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'teacher':
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    # වෙනත් ගුරුවරුන්ගේ පාඨමාලා වෙනස් කිරීම වැළැක්වීම
    if course.teacher_id != current_user.id:
        abort(403)
        
    form = CourseForm(obj=course) # දැනට ඇති දත්ත Form එකට පිරවීම
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('teacher.my_courses'))
        
    return render_template('teacher/edit_course.html', form=form, course=course)

@teacher_bp.route('/earnings')
@login_required
def earnings():
    if current_user.role != 'teacher':
        abort(403)
    
    # දැනට හිස් දත්ත යවමු (Payment ගොනු සැකසූ පසු මෙය යාවත්කාලීන කළ හැක)
    total_earnings = 0.00
    total_enrollments = 0
    transactions = []
    
    return render_template('teacher/earnings.html', 
                           total_earnings=total_earnings, 
                           total_enrollments=total_enrollments, 
                           transactions=transactions)
@teacher_bp.route('/bank-details', methods=['GET', 'POST'])
@login_required
def bank_details():
    if current_user.role != 'teacher':
        abort(403)
    
    form = BankDetailsForm()
    if form.validate_on_submit():
        current_user.bank_name = form.bank_name.data
        current_user.branch = form.branch.data
        current_user.account_name = form.account_name.data
        current_user.account_number = form.account_number.data
        db.session.commit()
        flash('Bank details updated successfully!', 'success')
        return redirect(url_for('teacher.bank_details'))
    
    if request.method == 'GET':
        form.bank_name.data = current_user.bank_name
        form.branch.data = current_user.branch
        form.account_name.data = current_user.account_name
        form.account_number.data = current_user.account_number
        
    return render_template('teacher/bank_details.html', form=form)    