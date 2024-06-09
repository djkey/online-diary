from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app, make_response

student_bp = Blueprint('student', __name__)


@student_bp.route('/schedule')
def student_schedule():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.group_id
            FROM Students s
            WHERE s.user_id = %s
        """, (user_id,))
        student = cursor.fetchone()

        if not student:
            return redirect(url_for('common.profile'))

        group_id = student['group_id']

        cursor.execute("""
            SELECT 
                sch.date, 
                sch.number_lesson,
                l.name AS lesson_name, 
                l.room_number, 
                t.user_id AS teacher_id
            FROM 
                Schedules sch
            JOIN 
                Lessons l ON sch.lesson_id = l.lesson_id
            JOIN 
                Teachers t ON l.teacher_id = t.teacher_id
            WHERE 
                sch.group_id = %s
            ORDER BY 
                sch.date, sch.number_lesson
        """, (group_id,))

        schedule = cursor.fetchall()

        for lesson in schedule:
            cursor.execute("""
                SELECT u.name AS teacher_name
                FROM Users u
                WHERE u.user_id = %s
            """, (lesson['teacher_id'],))
            teacher = cursor.fetchone()
            lesson['teacher_name'] = teacher['teacher_name']

    # Группировка по дате
    grouped_schedule = {}
    for lesson in schedule:
        date = lesson['date']
        if date not in grouped_schedule:
            grouped_schedule[date] = []
        grouped_schedule[date].append(lesson)

    return render_template('student/schedule.html', grouped_schedule=grouped_schedule)


@student_bp.route('/homework')
def student_homework():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.group_id
            FROM Students s
            WHERE s.user_id = %s
        """, (user_id,))
        student = cursor.fetchone()

        if not student:
            return redirect(url_for('common.profile'))

        group_id = student['group_id']

        cursor.execute("""
            SELECT 
                h.homework_id,
                h.description,
                h.date_to,
                COALESCE(s.submission_date, NULL) AS submission_date
            FROM 
                Homeworks h
            JOIN 
                Schedules sch ON h.homework_id = sch.homework_id
            LEFT JOIN 
                Solutions s ON h.homework_id = s.homework_id AND s.student_id = %s
            WHERE 
                sch.group_id = %s
            ORDER BY 
                h.date_to
        """, (user_id, group_id))

        homeworks = cursor.fetchall()

    return render_template('student/homework_list.html', homeworks=homeworks)


@student_bp.route('/homework/<int:homework_id>', methods=['GET', 'POST'])
def student_submit_homework(homework_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            description = request.form['description']
            file = request.files['files']
            filename = file.filename
            file_content = file.read()

            cursor.execute("""
                INSERT INTO Solutions (homework_id, student_id, description, files, data_options, submission_date)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                description = VALUES(description),
                files = VALUES(files),
                data_options = VALUES(data_options),
                submission_date = NOW()
            """, (homework_id, user_id, description, file_content, filename))
            current_app.connection.commit()
            flash('Домашнє завдання успішно здано!', 'success')

        cursor.execute("""
            SELECT 
                h.homework_id,
                h.description AS homework_description,
                h.date_to,
                s.description AS solution_description,
                s.files,
                s.data_options,
                s.submission_date
            FROM 
                Homeworks h
            LEFT JOIN 
                Solutions s ON h.homework_id = s.homework_id AND s.student_id = %s
            WHERE 
                h.homework_id = %s
        """, (user_id, homework_id))

        homework = cursor.fetchone()

    return render_template('student/homework_submit.html', homework=homework)


@student_bp.route('/homework/<int:homework_id>/download')
def download_file(homework_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT files, data_options 
            FROM Solutions 
            WHERE homework_id = %s AND student_id = %s
        """, (homework_id, user_id))

        solution = cursor.fetchone()

        if not solution:
            flash('Файл не знайдено', 'error')
            return redirect(url_for('student.student_submit_homework', homework_id=homework_id))

    response = make_response(solution['files'])
    response.headers.set('Content-Type', 'application/octet-stream')
    response.headers.set('Content-Disposition',
                        f'attachment; filename={solution["data_options"]}')

    return response
