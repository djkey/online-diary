from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    # Пример маршрута для администратора
    return render_template('admin/admin_dashboard.html')

# Другие маршруты для администратора...
