from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app

student_bp = Blueprint('student', __name__)


@student_bp.route('/student/dashboard')
def student_dashboard():
    # Пример маршрута для студента
    return render_template('student/student_dashboard.html')

# Другие маршруты для студента...
