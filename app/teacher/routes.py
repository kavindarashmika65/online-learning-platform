from flask import render_template, abort
from app.teacher import teacher_bp
from flask_login import login_required, current_user

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        abort(403)
    return render_template('teacher/dashboard.html')