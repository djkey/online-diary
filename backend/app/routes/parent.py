from flask import Blueprint, render_template, redirect, url_for, session, current_app
import pprint
from .decorators import parent_required

parent_bp = Blueprint('parent', __name__)


@parent_bp.route('/parent/grades')
@parent_required
def parent_grades():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('common.login'))

    with current_app.connection.cursor() as cursor:
        cursor.execute("""
            SELECT student_id 
            FROM Parents 
            WHERE user_id = %s
        """, (user_id,))
        student_ids = cursor.fetchall()

        grades_data = {}
        for student in student_ids:
            student_id = student['student_id']

            cursor.execute("""
                SELECT name 
                FROM Users 
                JOIN Students ON Users.user_id = Students.user_id 
                WHERE Students.student_id = %s
            """, (student_id,))
            student_name = cursor.fetchone()['name']

            cursor.execute("""
                SELECT 
                    Lessons.name AS lesson_name, 
                    Schedules.date
                FROM 
                    Schedules
                JOIN 
                    Lessons ON Schedules.lesson_id = Lessons.lesson_id
                WHERE 
                    Schedules.group_id IN (SELECT group_id FROM Students WHERE student_id = %s)
                ORDER BY 
                    Schedules.date;
            """, (student_id,))
            schedules = cursor.fetchall()

            cursor.execute("""
                SELECT 
                    Schedules.date, 
                    Grades.grade, 
                    Lessons.name AS lesson_name
                FROM 
                    Grades
                JOIN 
                    Schedules ON Grades.schedule_id = Schedules.schedule_id
                JOIN 
                    Lessons ON Schedules.lesson_id = Lessons.lesson_id
                WHERE 
                    Grades.student_id = %s
                ORDER BY 
                    Schedules.date;
            """, (student_id,))
            grades = cursor.fetchall()

            # Организация данных для отображения в таблице
            lessons = {}
            dates = sorted(list(set(schedule['date']
                           for schedule in schedules)))

            for schedule in schedules:
                lesson_name = schedule['lesson_name']
                date = schedule['date']
                if lesson_name not in lessons:
                    lessons[lesson_name] = {date: '' for date in dates}

            for grade in grades:
                lesson_name = grade['lesson_name']
                date = grade['date']
                lessons[lesson_name][date] = grade['grade']

            grades_data[student_name] = {
                'lessons': lessons,
                'dates': dates
            }

    return render_template('parent/parent_grades.html', grades_data=grades_data)
