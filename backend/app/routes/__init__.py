from .common import common_bp
from .admin import admin_bp
from .teacher import teacher_bp
from .student import student_bp
from .parent import parent_bp
from .admin_tables import tables_bp
from .download import download_bp

# Список всех Blueprint'ов для удобного импорта
blueprints = [
    common_bp,
    admin_bp,
    teacher_bp,
    student_bp,
    parent_bp,
    tables_bp,
    download_bp
]
