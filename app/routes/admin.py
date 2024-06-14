from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from .decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/new_users', methods=['GET', 'POST'])
@admin_required
def new_users():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            user_roles = request.form.getlist('role')
            user_ids = request.form.getlist('user_id')

            for user_id, role in zip(user_ids, user_roles):
                if role == 'student':
                    cursor.execute("INSERT INTO Students (user_id) VALUES (%s)", (user_id,))
                elif role == 'teacher':
                    cursor.execute("INSERT INTO Teachers (user_id) VALUES (%s)", (user_id,))
                elif role == 'parent':
                    cursor.execute("INSERT INTO Parents (user_id) VALUES (%s)", (user_id,))
                elif role == 'admin':
                    cursor.execute("INSERT INTO Admins (user_id) VALUES (%s)", (user_id,))

            current_app.connection.commit()
            return redirect(url_for('admin.new_users'))

        cursor.execute("""
            SELECT u.user_id, u.name, u.email
            FROM Users u
            LEFT JOIN Students s ON u.user_id = s.user_id
            LEFT JOIN Teachers t ON u.user_id = t.user_id
            LEFT JOIN Parents p ON u.user_id = p.user_id
            LEFT JOIN Admins a ON u.user_id = a.user_id
            WHERE s.user_id IS NULL AND t.user_id IS NULL AND p.user_id IS NULL AND a.user_id IS NULL
        """)
        new_users = cursor.fetchall()

    return render_template('admin/new_users.html', new_users=new_users)

@admin_bp.route('/admin/add_news', methods=['GET', 'POST'])
@admin_required
def add_news():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    if request.method == 'POST':
        role = request.form['role']
        notification = request.form['notification']

        with current_app.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Notifications (user_id, options, notifications)
                VALUES (%s, %s, %s)
            """, (current_user_id, role, notification))
            current_app.connection.commit()

        return redirect(url_for('admin.add_news'))

    return render_template('admin/add_news.html')

@admin_bp.route('/admin/tables', methods=['GET'])
@admin_required
def list_tables():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[f'Tables_in_{current_app.config["DB_NAME"]}'] for row in cursor.fetchall()]

    return render_template('admin/list_tables.html', tables=tables)
