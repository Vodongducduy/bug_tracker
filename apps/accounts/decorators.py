from django.shortcuts import redirect
from functools import wraps

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request, 'logged_user') or request.logged_user is None:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
