from functools import wraps
from flask import redirect, url_for, session, abort


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            abort(404)
        return f(*args, **kwargs)
    return decorated_function
