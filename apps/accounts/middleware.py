from django.core import signing
from .models import User

class ManualAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract user_id from signed cookie 'auth_session'
        user_id = None
        auth_cookie = request.get_signed_cookie('auth_session', default=None, salt='manual_auth')
        
        if auth_cookie:
            try:
                user_id = int(auth_cookie)
            except (ValueError, TypeError):
                user_id = None

        # Attach user to request
        request.logged_user = None
        if user_id:
            try:
                request.logged_user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
