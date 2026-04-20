from functools import wraps
from flask import g, redirect, url_for


def guest_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if getattr(g, "user", None):
            return redirect(url_for("auth.dashboard"))

        return view(*args, **kwargs)

    return wrapped_view