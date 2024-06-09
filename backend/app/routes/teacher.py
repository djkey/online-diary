from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/teacher/dashboard')
def teacher_dashboard():
    # Пример маршрута для учителя
    return render_template('teacher/teacher_dashboard.html')

# Другие маршруты для учителя...
