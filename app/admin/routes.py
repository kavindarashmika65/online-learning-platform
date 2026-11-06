from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.admin import admin_bp
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from sqlalchemy import func
from datetime import datetime
import calendar

def admin_required(func_name):
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return func_name(*args, **kwargs)
    wrapper.__name__ = func_name.__name__
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_courses = Course.query.count()
    
    approved_enrollments = Enrollment.query.filter_by(status='approved').all()
    total_earnings = sum(e.course.price for e in approved_enrollments)
    
    today = datetime.utcnow()
    month_labels = []
    revenue_by_month = {}
    students_by_month = {}
    teachers_by_month = {}

    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year + (today.month - i - 1) // 12
        m_label = f"{calendar.month_abbr[m]} {y}"
        month_labels.append(m_label)
        revenue_by_month[m_label] = 0.0
        students_by_month[m_label] = 0
        teachers_by_month[m_label] = 0

    for e in approved_enrollments:
        if e.enrollment_date:
            m_label = f"{calendar.month_abbr[e.enrollment_date.month]} {e.enrollment_date.year}"
            if m_label in revenue_by_month:
                revenue_by_month[m_label] += float(e.course.price)

    all_users = User.query.all()
    for u in all_users:
        if u.created_at:
            m_label = f"{calendar.month_abbr[u.created_at.month]} {u.created_at.year}"
            if m_label in students_by_month and u.role == 'student':
                students_by_month[m_label] += 1
            elif m_label in teachers_by_month and u.role == 'teacher':
                teachers_by_month[m_label] += 1

    top_courses_query = db.session.query(
        Course.title, func.count(Enrollment.id).label('total')
    ).join(Enrollment, Course.id == Enrollment.course_id, isouter=True)\
     .group_by(Course.id)\
     .order_by(func.count(Enrollment.id).desc()).limit(5).all()

    top_course_names = [c[0] for c in top_courses_query]
    top_course_counts = [c[1] for c in top_courses_query]

    return render_template('admin/dashboard.html', 
                           total_users=total_users, 
                           total_courses=total_courses, 
                           total_earnings=total_earnings,
                           month_labels=month_labels,
                           revenue_data=[revenue_by_month[m] for m in month_labels],
                           student_growth=[students_by_month[m] for m in month_labels],
                           teacher_growth=[teachers_by_month[m] for m in month_labels],
                           top_course_names=top_course_names,
                           top_course_counts=top_course_counts)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    # පසුගිය මාස 6 සඳහා ලියාපදිංචි වූ සිසුන් හා ගුරුවරුන් Database එකෙන් ගණනය කිරීම
    today = datetime.utcnow()
    month_labels = []
    student_counts = {}
    teacher_counts = {}

    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year + (today.month - i - 1) // 12
        m_label = f"{calendar.month_abbr[m]} {y}"
        month_labels.append(m_label)
        student_counts[m_label] = 0
        teacher_counts[m_label] = 0

    for u in all_users:
        if u.created_at:
            m_label = f"{calendar.month_abbr[u.created_at.month]} {u.created_at.year}"
            if m_label in student_counts and u.role == 'student':
                student_counts[m_label] += 1
            elif m_label in teacher_counts and u.role == 'teacher':
                teacher_counts[m_label] += 1

    return render_template('admin/users.html', 
                           users=all_users,
                           chart_labels=month_labels,
                           student_data=[student_counts[m] for m in month_labels],
                           teacher_data=[teacher_counts[m] for m in month_labels])

@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/course.html', courses=all_courses)

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    all_enrollments = Enrollment.query.order_by(Enrollment.enrollment_date.desc()).all()
    
    # පසුගිය මාස 6 සඳහා Approved වූ ආදායම Database එකෙන් ගණනය කිරීම
    today = datetime.utcnow()
    month_labels = []
    monthly_revenue = {}

    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year + (today.month - i - 1) // 12
        m_label = f"{calendar.month_abbr[m]} {y}"
        month_labels.append(m_label)
        monthly_revenue[m_label] = 0.0

    approved_enrollments = Enrollment.query.filter_by(status='approved').all()
    for e in approved_enrollments:
        if e.enrollment_date:
            m_label = f"{calendar.month_abbr[e.enrollment_date.month]} {e.enrollment_date.year}"
            if m_label in monthly_revenue:
                monthly_revenue[m_label] += float(e.course.price)

    return render_template('admin/payments.html', 
                           enrollments=all_enrollments,
                           chart_labels=month_labels,
                           chart_data=[monthly_revenue[m] for m in month_labels])