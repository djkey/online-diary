from functools import wraps
from flask import redirect, url_for, session, abort


def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            user_role = session.get('role')

            if not user_id:
                return redirect(url_for('common.login'))

            if user_role not in roles and user_role != 'admin':
                abort(404)  

            return f(*args, **kwargs)
        return decorated_function
    return decorator


teacher_required = role_required(['teacher'])
student_required = role_required(['student'])
parent_required = role_required(['parent'])
admin_required = role_required(['admin'])
