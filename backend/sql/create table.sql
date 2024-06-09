CREATE DATABASE diplom; --CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE diplom;

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE Admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    science_degree VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Classes (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class_teacher INT,
    start_year INT,
    FOREIGN KEY (class_teacher) REFERENCES Teachers(teacher_id)
);

CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    group_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (group_id) REFERENCES Classes(group_id)
);

CREATE TABLE Parents (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    student_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

CREATE TABLE Lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    room_number INT,
    teacher_id INT,
    description TEXT,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
);

CREATE TABLE Homeworks (
    homework_id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT,
    date_to DATE
);

CREATE TABLE Schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT,
    date DATE,
    number_lesson INT,
    lesson_id INT,
    homework_id INT,
    FOREIGN KEY (group_id) REFERENCES Classes(group_id),
    FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id),
    FOREIGN KEY (homework_id) REFERENCES Homeworks(homework_id)
);

CREATE TABLE Grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    schedule_id INT,
    grade TINYINT CHECK (grade BETWEEN 0 AND 12),
    comments TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedules(schedule_id)
);

CREATE TABLE Solutions (
    homework_id INT,
    student_id INT,
    description TEXT,
    files LONGBLOB,
    data_options TEXT,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (homework_id) REFERENCES Homeworks(homework_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

CREATE TABLE Notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    options TEXT,
    notifications TEXT,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    msg TEXT,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id)
);

SET FOREIGN_KEY_CHECKS = 1;
