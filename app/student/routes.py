from flask import render_template, abort
from app.student import student_bp
from flask_login import login_required, current_user

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        abort(403) # වෙනත් අයට ඇතුල් වීමට නොදෙයි
    return render_template('student/dashboard.html')