from app import db


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Admin(db.Model):
    __tablename__ = 'Admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))


class Teacher(db.Model):
    __tablename__ = 'Teachers'
    teacher_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    science_degree = db.Column(db.String(100))


class Class(db.Model):
    __tablename__ = 'Classes'
    group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_teacher = db.Column(db.Integer, db.ForeignKey('Teachers.teacher_id'))
    start_year = db.Column(db.Integer)


class Student(db.Model):
    __tablename__ = 'Students'
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    group_id = db.Column(db.Integer, db.ForeignKey('Classes.group_id'))


class Parent(db.Model):
    __tablename__ = 'Parents'
    parent_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('Students.student_id'))


class Lesson(db.Model):
    __tablename__ = 'Lessons'
    lesson_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    room_number = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey('Teachers.teacher_id'))
    description = db.Column(db.Text)


class Homework(db.Model):
    __tablename__ = 'Homeworks'
    homework_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    date_to = db.Column(db.Date)


class Schedule(db.Model):
    __tablename__ = 'Schedules'
    schedule_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('Classes.group_id'))
    date = db.Column(db.Date)
    number_lesson = db.Column(db.Integer)
    lesson_id = db.Column(db.Integer, db.ForeignKey('Lessons.lesson_id'))
    homework_id = db.Column(db.Integer, db.ForeignKey('Homeworks.homework_id'))


class Grade(db.Model):
    __tablename__ = 'Grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Students.student_id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('Schedules.schedule_id'))
    grade = db.Column(db.Integer, check='grade BETWEEN 0 AND 12')
    comments = db.Column(db.Text)


class Solution(db.Model):
    __tablename__ = 'Solutions'
    homework_id = db.Column(db.Integer, db.ForeignKey('Homeworks.homework_id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Students.student_id'), primary_key=True)
    description = db.Column(db.Text)
    files = db.Column(db.LargeBinary)
    data_options = db.Column(db.Text)
    submission_date = db.Column(db.DateTime, default=db.func.current_timestamp())


class Notification(db.Model):
    __tablename__ = 'Notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    options = db.Column(db.Text)
    notifications = db.Column(db.Text)
    submission_date = db.Column(db.DateTime, default=db.func.current_timestamp())


class Message(db.Model):
    __tablename__ = 'Messages'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    msg = db.Column(db.Text)
    submission_date = db.Column(db.DateTime, default=db.func.current_timestamp())
