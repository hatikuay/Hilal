from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def roles_required(*allowed_roles):
    """
    @roles_required('admin', 'moderator') şeklinde kullanılır.
    Sadece current_user.role, allowed_roles içinde ise devam eder,
    değilse 403 döner.
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
