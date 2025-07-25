# auction/middleware/session_user.py

from django.contrib.auth.models import AnonymousUser
from Auction.auth_backend import RawSQLAuthBackend

class RawSQLUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_backend = RawSQLAuthBackend()

    def __call__(self, request):
        user_id = request.session.get("user_id")
        user_type = request.session.get("user_type")
        if user_id:
            request.user = self.auth_backend.get_user(user_id, user_type)
        else:
            request.user = AnonymousUser()
        return self.get_response(request)
