from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app

common_bp = Blueprint('common', __name__)


@common_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('common/404.html'), 404

@common_bp.route('/')
def index():
    return render_template('common/index.html')


@common_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        with current_app.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Users WHERE email=%s OR login=%s", (data['email'], data['login']))
            user = cursor.fetchone()
            if user:
                return jsonify({'message': 'User already exists'}), 409
            cursor.execute(
                "INSERT INTO Users (name, email, login, password) VALUES (%s, %s, %s, %s)",
                (data['name'], data['email'], data['login'], data['password'])
            )
            current_app.connection.commit()
        return redirect(url_for('common.login'))
    return render_template('common/register.html')


@common_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        with current_app.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE login=%s",
                           (data['login'],))
            user = cursor.fetchone()
            if user and user['password'] == data['password']:
                session['user_id'] = user['user_id']
                # Определение роли пользователя
                cursor.execute(
                    "SELECT * FROM Admins WHERE user_id=%s", (user['user_id'],))
                if cursor.fetchone():
                    session['role'] = 'admin'
                else:
                    cursor.execute(
                        "SELECT * FROM Teachers WHERE user_id=%s", (user['user_id'],))
                    if cursor.fetchone():
                        session['role'] = 'teacher'
                    else:
                        cursor.execute(
                            "SELECT * FROM Students WHERE user_id=%s", (user['user_id'],))
                        if cursor.fetchone():
                            session['role'] = 'student'
                        else:
                            cursor.execute(
                                "SELECT * FROM Parents WHERE user_id=%s", (user['user_id'],))
                            if cursor.fetchone():
                                session['role'] = 'parent'
                            else:
                                session['role'] = 'user'
                return redirect(url_for('common.profile'))
            return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('common/login.html')


@common_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()
        role = session.get('role')

        group_name = ""
        children_info = ""

        if request.method == 'POST':
            if 'password' in request.form and 'confirm_password' in request.form:
                new_password = request.form['password']
                confirm_password = request.form['confirm_password']
                if new_password == confirm_password:
                    cursor.execute(
                        "UPDATE Users SET password=%s WHERE user_id=%s", (new_password, user_id))
                    current_app.connection.commit()
                    flash('Password updated successfully', 'success')
                else:
                    flash('Passwords do not match', 'error')
            elif 'delete_account' in request.form:
                cursor.execute(
                    "DELETE FROM Users WHERE user_id=%s", (user_id,))
                current_app.connection.commit()
                session.pop('user_id', None)
                session.pop('role', None)
                flash('Account deleted successfully', 'success')
                return redirect(url_for('common.index'))

        extra_info = user['name']
        if role == 'teacher':
            cursor.execute(
                "SELECT * FROM Teachers WHERE user_id=%s", (user_id,))
            teacher = cursor.fetchone()
            extra_info = f"{teacher['science_degree']} {user['name']}"
        elif role == 'student':
            cursor.execute(
                "SELECT * FROM Students WHERE user_id=%s", (user_id,))
            student = cursor.fetchone()
            cursor.execute(
                "SELECT * FROM Classes WHERE group_id=%s", (student['group_id'],))
            group = cursor.fetchone()
            group_name = group['name']
        elif role == 'parent':
            cursor.execute("""
                SELECT Users.name AS student_name 
                FROM Users 
                JOIN Students ON Users.user_id = Students.user_id 
                WHERE Students.student_id IN (
                    SELECT student_id 
                    FROM Parents 
                    WHERE user_id = %s
                )
            """, (user_id,))
            children = cursor.fetchall()
            children_info = ", ".join([child['student_name']
                                    for child in children])
        elif role == 'user':
            extra_info = f"{user['name']}"

    return render_template('common/profile.html', user=user, extra_info=extra_info, role=role, group_name=group_name, children_info=children_info)


@common_bp.route('/news')
def news():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    role = session.get('role')

    with current_app.connection.cursor() as cursor:
        if role == 'admin':
            cursor.execute("""
                SELECT notifications, submission_date 
                FROM Notifications 
                ORDER BY submission_date DESC
            """)
        else:
            cursor.execute("""
            SELECT notifications, submission_date 
            FROM Notifications 
            WHERE options = 'all' 
               OR options = %s
            ORDER BY submission_date DESC
            """, (role+"s",))
        notifications = cursor.fetchall()

    return render_template('common/news.html', notifications=notifications)


@common_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('common.login'))


# @common_bp.route('/users')
# def users():
#     with current_app.connection.cursor() as cursor:
#         cursor.execute("SELECT * FROM Users")
#         all_users = cursor.fetchall()
#     return render_template('common/users.html', users=all_users)

@common_bp.route('/users')
def users():
    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                u.user_id, 
                u.name, 
                u.email, 
                u.login, 
                u.password, 
                CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_admin, 
                CASE WHEN t.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_teacher, 
                CASE WHEN s.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_student, 
                CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_parent
            FROM Users u
            LEFT JOIN Admins a ON u.user_id = a.user_id
            LEFT JOIN Teachers t ON u.user_id = t.user_id
            LEFT JOIN Students s ON u.user_id = s.user_id
            LEFT JOIN Parents p ON u.user_id = p.user_id
        """)
        all_users = cursor.fetchall()
    return render_template('common/users.html', users=all_users)


@common_bp.route('/chat')
def chat_list():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT u.user_id, u.name 
            FROM Users u
            JOIN Messages m ON (u.user_id = m.sender_id OR u.user_id = m.receiver_id)
            WHERE m.sender_id = %s OR m.receiver_id = %s
        """, (user_id, user_id))

        contacts = cursor.fetchall()

    return render_template('chat/chat_list.html', contacts=contacts)


@common_bp.route('/chat/<int:user_id>', methods=['GET', 'POST'])
def chat(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            message = request.form['message']
            cursor.execute("""
                INSERT INTO Messages (sender_id, receiver_id, msg)
                VALUES (%s, %s, %s)
            """, (current_user_id, user_id, message))
            current_app.connection.commit()

        cursor.execute("""
            SELECT m.msg, m.submission_date, u.name as sender_name, m.sender_id
            FROM Messages m
            JOIN Users u ON m.sender_id = u.user_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s) OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.submission_date
        """, (current_user_id, user_id, user_id, current_user_id))

        messages = cursor.fetchall()

        cursor.execute("""
            SELECT name FROM Users WHERE user_id = %s
        """, (user_id,))
        recipient_name = cursor.fetchone()['name']

    return render_template('chat/chat.html', messages=messages, user_id=user_id, recipient_name=recipient_name)


@common_bp.route('/chat/new', methods=['GET', 'POST'])
def new_chat():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            receiver_id = request.form['receiver_id']
            return redirect(url_for('common.chat', user_id=receiver_id))

        cursor.execute("""
            SELECT user_id, name FROM Users WHERE user_id != %s
        """, (current_user_id,))

        users = cursor.fetchall()

    return render_template('chat/new_chat.html', users=users)

