from flask import render_template, session, redirect, url_for, current_app, Blueprint, request
from datetime import datetime
from .decorators import teacher_required

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/teacher/schedule', methods=['GET', 'POST'])
@teacher_required
def teacher_schedule():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        # Получаем список групп, которыми руководит текущий учитель
        cursor.execute("""
            SELECT c.group_id, c.name as group_name
            FROM Classes c
            JOIN Teachers t ON c.class_teacher = t.teacher_id
            WHERE t.user_id = %s
        """, (current_user_id,))
        groups = cursor.fetchall()

        # Получаем все возможные предметы
        cursor.execute("SELECT lesson_id, name FROM Lessons")
        all_lessons = cursor.fetchall()

        # Получаем расписание для каждой группы
        schedules = {}
        for group in groups:
            cursor.execute("""
                SELECT s.schedule_id, s.date, l.name as lesson_name, l.lesson_id, s.number_lesson, 
                    u.name as teacher_name, l.room_number, l.description as lesson_description
                FROM Schedules s
                LEFT JOIN Lessons l ON s.lesson_id = l.lesson_id
                LEFT JOIN Teachers t ON l.teacher_id = t.teacher_id
                LEFT JOIN Users u ON t.user_id = u.user_id
                WHERE s.group_id = %s
                ORDER BY s.date, s.number_lesson
            """, (group['group_id'],))
            group_schedule = cursor.fetchall()

            # Группируем расписание по дате, фильтруя прошедшие дни
            grouped_schedule = {}
            today = datetime.today().date()
            for entry in group_schedule:
                entry_date = entry['date']
                if entry_date >= today:
                    if entry_date not in grouped_schedule:
                        grouped_schedule[entry_date] = [
                            None] * 8  # 8 возможных уроков за день
                    grouped_schedule[entry_date][entry['number_lesson'] - 1] = entry
            schedules[group['group_name']] = grouped_schedule

        # Если это POST запрос, обрабатываем изменения расписания или добавление нового дня
        if request.method == 'POST':
            if 'add_day' in request.form:
                group_id = request.form.get('group_id')
                date = request.form.get('date')
                if group_id and date:
                    for i in range(1, 9):
                        cursor.execute("""
                            INSERT INTO Schedules (group_id, date, number_lesson)
                            VALUES (%s, %s, %s)
                        """, (group_id, date, i))
                    current_app.connection.commit()
            else:
                schedule_id = request.form.get('schedule_id')
                lesson_id = request.form.get('lesson_id')
                group_id = request.form.get('group_id')
                date = request.form.get('date')
                number_lesson = request.form.get('number_lesson')

                print(f"Received POST data: schedule_id={schedule_id}, lesson_id={
                    lesson_id}, group_id={group_id}, date={date}, number_lesson={number_lesson}")

                if lesson_id:
                    if schedule_id:
                        cursor.execute("""
                            UPDATE Schedules
                            SET lesson_id = %s
                            WHERE schedule_id = %s
                        """, (lesson_id, schedule_id))
                        print(f"Updated schedule with schedule_id={
                            schedule_id}, lesson_id={lesson_id}")
                    else:
                        cursor.execute("""
                            INSERT INTO Schedules (group_id, date, number_lesson, lesson_id)
                            VALUES (%s, %s, %s, %s)
                        """, (group_id, date, number_lesson, lesson_id))
                        print(f"Inserted new schedule for group_id={group_id}, date={
                            date}, number_lesson={number_lesson}, lesson_id={lesson_id}")
                else:
                    if schedule_id:
                        cursor.execute("""
                            DELETE FROM Schedules
                            WHERE schedule_id = %s
                        """, (schedule_id,))
                        print(f"Deleted schedule with schedule_id={
                                schedule_id}")
                current_app.connection.commit()
            return redirect(url_for('teacher.teacher_schedule'))

    return render_template('teacher/schedule.html', groups=groups, schedules=schedules, all_lessons=all_lessons)


@teacher_bp.route('/teacher/my_subject', methods=['GET', 'POST'])
@teacher_required
def my_subject():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        # Получаем все уроки, которые ведет текущий учитель
        cursor.execute("""
            SELECT l.lesson_id, l.name as lesson_name, c.name as group_name, s.date, s.schedule_id
            FROM Schedules s
            JOIN Lessons l ON s.lesson_id = l.lesson_id
            JOIN Classes c ON s.group_id = c.group_id
            JOIN Teachers t ON l.teacher_id = t.teacher_id
            WHERE t.user_id = %s
            ORDER BY s.date
        """, (current_user_id,))
        lessons = cursor.fetchall()

        grouped_lessons = {}
        for lesson in lessons:
            lesson_date = lesson['date']
            if lesson_date not in grouped_lessons:
                grouped_lessons[lesson_date] = []
            grouped_lessons[lesson_date].append(lesson)

    return render_template('teacher/my_subject.html', grouped_lessons=grouped_lessons)


@teacher_bp.route('/teacher/my_subject/<int:schedule_id>', methods=['GET', 'POST'])
@teacher_required
def view_grades(schedule_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        # Получаем информацию о занятии
        cursor.execute("""
            SELECT c.name as group_name, l.name as lesson_name, s.date, s.schedule_id, s.homework_id
            FROM Schedules s
            JOIN Lessons l ON s.lesson_id = l.lesson_id
            JOIN Classes c ON s.group_id = c.group_id
            WHERE s.schedule_id = %s
        """, (schedule_id,))
        lesson = cursor.fetchone()

        # Получаем список учеников и их оценок
        cursor.execute("""
            SELECT s.student_id, u.name as student_name, g.grade, g.comments
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
            LEFT JOIN Grades g ON s.student_id = g.student_id AND g.schedule_id = %s
            WHERE s.group_id = (SELECT group_id FROM Schedules WHERE schedule_id = %s)
        """, (schedule_id, schedule_id))
        students = cursor.fetchall()

        # Получаем список домашних заданий
        cursor.execute("SELECT homework_id, description FROM Homeworks")
        homeworks = cursor.fetchall()

        if request.method == 'POST':
            homework_id = request.form.get('homework_id')

            # Обновление оценок и комментариев
            for student in students:
                student_id = student['student_id']
                grade = request.form.get(f'grade_{student_id}')
                comment = request.form.get(f'comment_{student_id}')

                if grade == '':
                    grade = None
                else:
                    grade = int(grade)

                cursor.execute("""
                    INSERT INTO Grades (student_id, schedule_id, grade, comments)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE grade = VALUES(grade), comments = VALUES(comments)
                """, (student_id, schedule_id, grade, comment))

            # Назначение домашнего задания
            if homework_id:
                cursor.execute("""
                    UPDATE Schedules
                    SET homework_id = %s
                    WHERE schedule_id = %s
                """, (homework_id, schedule_id))

            current_app.connection.commit()
            return redirect(url_for('teacher.view_grades', schedule_id=schedule_id))

    return render_template('teacher/view_grades.html', students=students, lesson=lesson, homeworks=homeworks)


@teacher_bp.route('/teacher/solution/<int:homework_id>/<int:student_id>', methods=['GET'])
@teacher_required
def view_solution(homework_id, student_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.description, s.files, s.submission_date, u.name as student_name, h.description as homework_description
            FROM Solutions s
            JOIN Users u ON s.student_id = u.user_id
            JOIN Homeworks h ON s.homework_id = h.homework_id
            WHERE s.homework_id = %s AND s.student_id = %s
        """, (homework_id, student_id))
        solution = cursor.fetchone()

    return render_template('teacher/view_solution.html', solution=solution)


@teacher_bp.route('/homework/<int:homework_id>/download/<int:student_id>', methods=['GET'])
@teacher_required
def download_file(homework_id, student_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT files, data_options
            FROM Solutions
            WHERE homework_id = %s AND student_id = %s
        """, (homework_id, student_id))
        solution = cursor.fetchone()

        if not solution:
            return "File not found", 404

        file_data = solution['files']
        file_name = solution['data_options']

    return send_file(
        BytesIO(file_data),
        download_name=file_name,
        as_attachment=True
    )


@teacher_bp.route('/teacher/homeworks', methods=['GET', 'POST'])
@teacher_required
def homeworks():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        if request.method == 'POST':
            description = request.form['description']
            date_to = request.form['date_to']
            cursor.execute("""
                INSERT INTO Homeworks (description, date_to)
                VALUES (%s, %s)
            """, (description, date_to))
            current_app.connection.commit()

        cursor.execute("""
            SELECT homework_id, description, date_to
            FROM Homeworks
            ORDER BY date_to DESC
        """)
        homeworks = cursor.fetchall()

    return render_template('teacher/homeworks.html', homeworks=homeworks)
