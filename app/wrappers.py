from functools import wraps
import base64

from flask import session, redirect, url_for, request, flash
from app.infra_module.models import UserM
from app.infra_module.other import UserRole


def _redirect_to_login():
    if UserM.needs_setup():
        return redirect(url_for("infra_module.setup"))

    requestUrl = request.url
    requested_url = "/" + "/".join(requestUrl.split("/")[3:])
    encoded = base64.urlsafe_b64encode(requested_url.encode()).decode()
    flash("Please login to access the site.", "error")
    return redirect(url_for("infra_module.login", w_url=encoded))


def access_required(min_role: UserRole = None):
    """
    Decorator that enforces authentication and optional role requirement.

    Usage:
        @access_required()                      # any logged-in active user
        @access_required(UserRole.READWRITE)    # readwrite or admin
        @access_required(UserRole.ADMIN)        # admin only
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return _redirect_to_login()

            user = UserM.get_one(session['user_id'])
            if not user or user.get('status') != 1:
                session.clear()
                return _redirect_to_login()

            if min_role is None:
                return f(*args, **kwargs)

            user_role = UserRole(user['role'])
            # Lower value = more access: ADMIN=1, READWRITE=2, READ=3
            if user_role.value <= min_role.value:
                return f(*args, **kwargs)

            flash("You don't have access to this page.", "error")
            return redirect(url_for("infra_module.index"))

        return wrapper
    return decorator


def login_required(f):
    """Simpler decorator: just requires any active login."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            user = UserM.get_one(session['user_id'])
            if user and user.get('status') == 1:
                return f(*args, **kwargs)
        return _redirect_to_login()
    return wrapper
