class User:
    def __init__(self, user_id, username, user_type=None, authenticated=True, anonymous=False, active = True, staff=False, superuser=False):
        self.id = user_id
        self.username = username
        self.user_type = user_type

        self._is_authenticated = authenticated
        self._is_anonymous = anonymous
        self._is_active = active
        self._is_staff = staff
        self._is_superuser = superuser
        self._meta = type("Meta", (), {
            "model_name": "user",
            "app_label": "custom_auth",
            "pk": type("PK", (), {
                "name": "id",
                "attname": "id",
                "get_pk_value_on_save": lambda instance: instance.id,
                "to_python": lambda val: int(val),
                "get_db_prep_value": lambda self, val, connection, prepared=False: val,
                "value_to_string": lambda self, instance: str(getattr(instance, self.name))
            })()
        })()   
    @property
    def pk(self):
        return self.id 
    

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value):
        self._is_authenticated = value
    

    @property
    def is_anonymous(self):
        return self._is_anonymous
    
    @property
    def is_active(self):
        return self._is_active
    @property
    def is_staff(self):
        return self._is_staff

    @property
    def is_superuser(self):
        return self._is_superuser

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        pass
