from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from flask import Blueprint, request, redirect, url_for, current_app, session, render_template
from .decorators import admin_required

tables_bp = Blueprint('tables', __name__)


@tables_bp.route('/admin/tables/old', methods=['GET'])
@admin_required
def list_tables_old():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[f'Tables_in_{current_app.config["DB_NAME"]}']
                for row in cursor.fetchall()]
        table_data = {}

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            table_data[table] = {
                'columns': columns,
                'rows': rows
            }

    return render_template('admin/list_tables_old.html', tables=tables, table_data=table_data)


@tables_bp.route('/admin/tables/admins', methods=['GET', 'POST'])
def view_admins():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    if request.method == 'POST':
        user_id = request.form['user_id']
        with current_app.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Admins (user_id) VALUES (%s)", (user_id,))
            current_app.connection.commit()
        return redirect(url_for('tables.view_admins'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Admins")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT u.user_id, u.name
            FROM Users u
            LEFT JOIN Admins a ON u.user_id = a.user_id
            LEFT JOIN Teachers t ON u.user_id = t.user_id
            LEFT JOIN Students s ON u.user_id = s.user_id
            LEFT JOIN Parents p ON u.user_id = p.user_id
            WHERE a.user_id IS NULL AND t.user_id IS NULL AND s.user_id IS NULL AND p.user_id IS NULL
        """)
        available_users = cursor.fetchall()

    return render_template('admin/tables/admins.html', columns=columns, rows=rows, available_users=available_users)


@tables_bp.route('/admin/tables/users', methods=['GET', 'POST'])
def view_users():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        login = request.form['login']
        password = request.form['password']
        with current_app.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Users (name, email, login, password)
                VALUES (%s, %s, %s, %s)
            """, (name, email, login, password))
            current_app.connection.commit()
        return redirect(url_for('tables.view_users'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

    return render_template('admin/tables/users.html', columns=columns, rows=rows)


@tables_bp.route('/admin/tables/teachers', methods=['GET', 'POST'])
def view_teachers():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    if request.method == 'POST':
        user_id = request.form['user_id']
        science_degree = request.form['science_degree']
        with current_app.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Teachers (user_id, science_degree)
                VALUES (%s, %s)
            """, (user_id, science_degree))
            current_app.connection.commit()
        return redirect(url_for('tables.view_teachers'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Teachers")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT u.user_id, u.name
            FROM Users u
            LEFT JOIN Admins a ON u.user_id = a.user_id
            LEFT JOIN Teachers t ON u.user_id = t.user_id
            LEFT JOIN Students s ON u.user_id = s.user_id
            LEFT JOIN Parents p ON u.user_id = p.user_id
            WHERE a.user_id IS NULL AND t.user_id IS NULL AND s.user_id IS NULL AND p.user_id IS NULL
        """)
        available_users = cursor.fetchall()

    return render_template('admin/tables/teachers.html', columns=columns, rows=rows, available_users=available_users)


@tables_bp.route('/admin/tables/students', methods=['GET', 'POST'])
def view_students():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    if request.method == 'POST':
        user_id = request.form['user_id']
        group_id = request.form['group_id']
        with current_app.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Students (user_id, group_id)
                VALUES (%s, %s)
            """, (user_id, group_id))
            current_app.connection.commit()
        return redirect(url_for('tables.view_students'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Students")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT u.user_id, u.name
            FROM Users u
            LEFT JOIN Admins a ON u.user_id = a.user_id
            LEFT JOIN Teachers t ON u.user_id = t.user_id
            LEFT JOIN Students s ON u.user_id = s.user_id
            LEFT JOIN Parents p ON u.user_id = p.user_id
            WHERE a.user_id IS NULL AND t.user_id IS NULL AND s.user_id IS NULL AND p.user_id IS NULL
        """)
        available_users = cursor.fetchall()

        cursor.execute("SELECT * FROM Classes")
        available_groups = cursor.fetchall()

    return render_template('admin/tables/students.html', columns=columns, rows=rows, available_users=available_users, available_groups=available_groups)


@tables_bp.route('/admin/tables/parents', methods=['GET', 'POST'])
def view_parents():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    if request.method == 'POST':
        user_id = request.form['user_id']
        student_id = request.form['student_id']
        with current_app.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Parents (user_id, student_id)
                VALUES (%s, %s)
            """, (user_id, student_id))
            current_app.connection.commit()
        return redirect(url_for('tables.view_parents'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Parents")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT u.user_id, u.name
            FROM Users u
            LEFT JOIN Admins a ON u.user_id = a.user_id
            LEFT JOIN Teachers t ON u.user_id = t.user_id
            LEFT JOIN Students s ON u.user_id = s.user_id
            LEFT JOIN Parents p ON u.user_id = p.user_id
            WHERE a.user_id IS NULL AND t.user_id IS NULL AND s.user_id IS NULL AND p.user_id IS NULL
        """)
        available_users = cursor.fetchall()

        cursor.execute("""
            SELECT s.student_id, u.name
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
        """)
        available_students = cursor.fetchall()

    return render_template('admin/tables/parents.html', columns=columns, rows=rows, available_users=available_users, available_students=available_students)


@tables_bp.route('/admin/tables/classes', methods=['GET', 'POST'])
def view_classes():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            name = request.form.get('name')
            class_teacher = request.form.get('class_teacher')
            start_year = request.form.get('start_year')

            if name and class_teacher and start_year:
                cursor.execute("""
                    INSERT INTO Classes (name, class_teacher, start_year)
                    VALUES (%s, %s, %s)
                """, (name, class_teacher, start_year))
                current_app.connection.commit()
            else:
                class_id = request.form.get('class_id')
                if class_id:
                    cursor.execute(
                        "DELETE FROM Classes WHERE class_id = %s", (class_id,))
                    current_app.connection.commit()

        cursor.execute("SELECT * FROM Classes")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT t.teacher_id, u.name
            FROM Teachers t
            JOIN Users u ON t.user_id = u.user_id
        """)
        available_teachers = cursor.fetchall()

    return render_template('admin/tables/classes.html', columns=columns, rows=rows, available_teachers=available_teachers)


@tables_bp.route('/admin/tables/grades', methods=['GET', 'POST'])
def view_grades():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            schedule_id = request.form.get('schedule_id')
            grade = request.form.get('grade')
            comments = request.form.get('comments')

            if student_id and schedule_id and grade:
                cursor.execute("""
                    INSERT INTO Grades (student_id, schedule_id, grade, comments)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, schedule_id, grade, comments))
                current_app.connection.commit()
            else:
                grade_id = request.form.get('grade_id')
                if grade_id:
                    cursor.execute(
                        "DELETE FROM Grades WHERE grade_id = %s", (grade_id,))
                    current_app.connection.commit()

        cursor.execute("SELECT * FROM Grades")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT s.student_id, u.name 
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
        """)
        available_students = cursor.fetchall()

        cursor.execute("SELECT schedule_id, date, number_lesson FROM Schedules")
        available_schedules = cursor.fetchall()

    return render_template('admin/tables/grades.html', columns=columns, rows=rows, available_students=available_students, available_schedules=available_schedules)


@tables_bp.route('/admin/tables/homeworks', methods=['GET', 'POST'])
def view_homeworks():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            description = request.form['description']
            date_to = request.form['date_to']
            cursor.execute(
                "INSERT INTO Homeworks (description, date_to) VALUES (%s, %s)", (description, date_to))
            current_app.connection.commit()

        cursor.execute("SELECT * FROM Homeworks")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

    return render_template('admin/tables/homeworks.html', columns=columns, rows=rows)


@tables_bp.route('/admin/tables/lessons', methods=['GET', 'POST'])
def view_lessons():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            name = request.form['name']
            room_number = request.form['room_number']
            teacher_id = request.form['teacher_id']
            description = request.form['description']
            cursor.execute("INSERT INTO Lessons (name, room_number, teacher_id, description) VALUES (%s, %s, %s, %s)",
                        (name, room_number, teacher_id, description))
            current_app.connection.commit()

        cursor.execute(
            "SELECT l.*, u.name as user_name FROM Lessons l JOIN Teachers t ON l.teacher_id = t.teacher_id JOIN Users u ON t.user_id = u.user_id")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute(
            "SELECT t.teacher_id, u.name as user_name FROM Teachers t JOIN Users u ON t.user_id = u.user_id")
        teachers = cursor.fetchall()

    return render_template('admin/tables/lessons.html', columns=columns, rows=rows, teachers=teachers)


@tables_bp.route('/admin/tables/messages', methods=['GET', 'POST'])
def view_messages():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            sender_id = request.form['sender_id']
            receiver_id = request.form['receiver_id']
            msg = request.form['msg']
            cursor.execute(
                "INSERT INTO Messages (sender_id, receiver_id, msg) VALUES (%s, %s, %s)", (sender_id, receiver_id, msg))
            current_app.connection.commit()

        cursor.execute("SELECT m.*, su.name as sender_name, ru.name as receiver_name FROM Messages m JOIN Users su ON m.sender_id = su.user_id JOIN Users ru ON m.receiver_id = ru.user_id")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("SELECT user_id, name FROM Users")
        users = cursor.fetchall()

    return render_template('admin/tables/messages.html', columns=columns, rows=rows, users=users)


@tables_bp.route('/admin/tables/notifications', methods=['GET', 'POST'])
def view_notifications():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            user_id = request.form['user_id']
            options = request.form['options']
            notifications = request.form['notifications']
            cursor.execute("INSERT INTO Notifications (user_id, options, notifications) VALUES (%s, %s, %s)",
                        (user_id, options, notifications))
            current_app.connection.commit()

        cursor.execute(
            "SELECT n.*, u.name as user_name FROM Notifications n JOIN Users u ON n.user_id = u.user_id")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("SELECT user_id, name FROM Users")
        users = cursor.fetchall()

    return render_template('admin/tables/notifications.html', columns=columns, rows=rows, users=users)


@tables_bp.route('/admin/tables/schedules', methods=['GET', 'POST'])
def view_schedules():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            group_id = request.form['group_id']
            date = request.form['date']
            number_lesson = request.form['number_lesson']
            lesson_id = request.form['lesson_id']
            homework_id = request.form.get('homework_id')
            cursor.execute("""
                INSERT INTO Schedules (group_id, date, number_lesson, lesson_id, homework_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (group_id, date, number_lesson, lesson_id, homework_id if homework_id else None))
            current_app.connection.commit()

        cursor.execute(
            "SELECT s.*, g.name as group_name, l.name as lesson_name FROM Schedules s JOIN Classes g ON s.group_id = g.group_id JOIN Lessons l ON s.lesson_id = l.lesson_id")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("SELECT group_id, name FROM Classes")
        groups = cursor.fetchall()

        cursor.execute("SELECT lesson_id, name FROM Lessons")
        lessons = cursor.fetchall()

        cursor.execute("SELECT homework_id, description FROM Homeworks")
        homeworks = cursor.fetchall()

    return render_template('admin/tables/schedules.html', columns=columns, rows=rows, groups=groups, lessons=lessons, homeworks=homeworks)


@tables_bp.route('/admin/tables/solutions', methods=['GET', 'POST'])
def view_solutions():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            homework_id = request.form['homework_id']
            student_id = request.form['student_id']
            description = request.form['description']
            file = request.files['files']
            file_data = file.read()
            file_name = file.filename

            cursor.execute("""
                INSERT INTO Solutions (homework_id, student_id, description, files, data_options)
                VALUES (%s, %s, %s, %s, %s)
            """, (homework_id, student_id, description, file_data, file_name))
            current_app.connection.commit()

        cursor.execute("""
            SELECT s.*, h.description as homework_desc, u.name as student_name 
            FROM Solutions s 
            JOIN Homeworks h ON s.homework_id = h.homework_id 
            JOIN Users u ON s.student_id = u.user_id
        """)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.execute("SELECT homework_id, description FROM Homeworks")
        homeworks = cursor.fetchall()

        cursor.execute("""
            SELECT s.student_id, u.name 
            FROM Students s 
            JOIN Users u ON s.user_id = u.user_id
        """)
        students = cursor.fetchall()

    return render_template('admin/tables/solutions.html', columns=columns, rows=rows, homeworks=homeworks, students=students)

# --------------------------------------------------------------------------
# Deleting
# --------------------------------------------------------------------------

@tables_bp.route('/admin/tables/admins/delete', methods=['POST'])
def delete_admin():
    admin_id = request.form['admin_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute("DELETE FROM Admins WHERE admin_id = %s", (admin_id,))
        current_app.connection.commit()
    return redirect(url_for('tables.view_admins'))


@tables_bp.route('/admin/tables/users/delete', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        current_app.connection.commit()
    return redirect(url_for('tables.view_users'))


@tables_bp.route('/admin/tables/teachers/delete', methods=['POST'])
def delete_teacher():
    teacher_id = request.form['teacher_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Teachers WHERE teacher_id = %s", (teacher_id,))
        current_app.connection.commit()
    return redirect(url_for('tables.view_teachers'))


@tables_bp.route('/admin/tables/students/delete', methods=['POST'])
def delete_student():
    student_id = request.form['student_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Students WHERE student_id = %s", (student_id,))
        current_app.connection.commit()
    return redirect(url_for('tables.view_students'))


@tables_bp.route('/admin/tables/parents/delete', methods=['POST'])
def delete_parent():
    parent_id = request.form['parent_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Parents WHERE parent_id = %s", (parent_id,))
        current_app.connection.commit()
    return redirect(url_for('tables.view_parents'))


@tables_bp.route('/admin/tables/classes/delete', methods=['POST'])
def delete_class():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    class_id = request.form.get('class_id')
    if class_id:
        with current_app.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Classes WHERE class_id = %s", (class_id,))
            current_app.connection.commit()

    return redirect(url_for('tables.view_classes'))


@tables_bp.route('/admin/tables/grades/delete', methods=['POST'])
def delete_grade():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    grade_id = request.form.get('grade_id')
    if grade_id:
        with current_app.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Grades WHERE grade_id = %s", (grade_id,))
            current_app.connection.commit()

    return redirect(url_for('tables.view_grades'))


@tables_bp.route('/admin/tables/homeworks/delete', methods=['POST'])
def delete_homework():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    homework_id = request.form['homework_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Homeworks WHERE homework_id = %s", (homework_id,))
        current_app.connection.commit()

    return redirect(url_for('tables.view_homeworks'))


@tables_bp.route('/admin/tables/lessons/delete', methods=['POST'])
def delete_lesson():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    lesson_id = request.form['lesson_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Lessons WHERE lesson_id = %s", (lesson_id,))
        current_app.connection.commit()

    return redirect(url_for('tables.view_lessons'))


@tables_bp.route('/admin/tables/messages/delete', methods=['POST'])
def delete_message():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    message_id = request.form['message_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Messages WHERE message_id = %s", (message_id,))
        current_app.connection.commit()

    return redirect(url_for('tables.view_messages'))


@tables_bp.route('/admin/tables/notifications/delete', methods=['POST'])
def delete_notification():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    notification_id = request.form['notification_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Notifications WHERE notification_id = %s", (notification_id,))
        current_app.connection.commit()

    return redirect(url_for('tables.view_notifications'))


@tables_bp.route('/admin/tables/schedules/delete', methods=['POST'])
def delete_schedule():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    schedule_id = request.form['schedule_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Schedules WHERE schedule_id = %s", (schedule_id,))
        current_app.connection.commit()

    return redirect(url_for('tables.view_schedules'))


@tables_bp.route('/admin/tables/solutions/delete', methods=['POST'])
def delete_solution():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    homework_id = request.form['homework_id']
    student_id = request.form['student_id']
    with current_app.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Solutions WHERE homework_id = %s AND student_id = %s", (homework_id, student_id))
        current_app.connection.commit()

    return redirect(url_for('tables.view_solutions'))

