from functools import wraps
from django.shortcuts import redirect


def logout_required(logout_redirect):
    def deco_logout(f):
        @wraps(f)
        def logout(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(logout_redirect)
            return f(request, *args, **kwargs)

        return logout

    return deco_logout
