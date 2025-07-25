from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db import connection
from django.contrib.auth.models import AnonymousUser
from .custom_user import User

class RawSQLAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, user_type=None):
        with connection.cursor() as cursor:
            if user_type=="Organization":
                cursor.execute("SELECT reg_no, name, password FROM organization WHERE reg_no = %s", [username])
            else:
                cursor.execute("SELECT citizenship_no, name, password FROM bidder WHERE citizenship_no = %s", [username])
            result = cursor.fetchone()
            if result and check_password(password, result[2]):
                user = User(result[0], result[1],user_type)
                user.is_authenticated = True
                return user
        return None

    def get_user(self, user_id, user_type):
        with connection.cursor() as cursor:
            if user_type=="Organization":
                cursor.execute("SELECT reg_no, name, password FROM organization WHERE reg_no = %s", [user_id])
            else:
                cursor.execute("SELECT citizenship_no, name, password FROM bidder WHERE citizenship_no = %s", [user_id])
            result = cursor.fetchone()
            if result:
                user = User(user_id,result[1], user_type)
                user.is_authenticated = True
                return user
        return None