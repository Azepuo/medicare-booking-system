from functools import wraps
from flask import redirect, url_for
from flask_login import current_user, login_required

def role_required(role):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            user_id = current_user.get_id()

            # utilisateur déconnecté
            if user_id is None:
                return redirect(url_for("auth.login_page"))

            user_role = user_id.split(":")[0]

            if user_role != role:
                return redirect(url_for("auth.login_page"))

            return fn(*args, **kwargs)

        return wrapper
    return decorator
