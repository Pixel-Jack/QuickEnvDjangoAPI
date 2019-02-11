from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class AuthenticationModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    You can choose to authenticate with login which will check in the field username and email.
    Order of check: login > email > username. If one is given the others won't be checked.
    If you know that you want to be logged by email or username we recommend
    to use authenticate(username=...) or authenticate(email=...) instead of login that would be faster.
    """

    def authenticate(self, request, username=None, password=None, email=None, login=None, **kwargs):
        email_value = email or kwargs.get(UserModel.EMAIL_FIELD)
        if login:
            # WARNING: We highly recommend to forbid the use of an email in the 'username' field
            # Otherwise technically a given email address could be present in field 'email' and 'username,
            # possibly even for different users, so we'll query for all matching
            # records and test each one. The first one will be log if they have the same password (Highly unlikely).
            users = UserModel._default_manager.filter(
                Q(**{UserModel.USERNAME_FIELD: login}) | Q(**{UserModel.EMAIL_FIELD: login})
            )
        elif email_value:
            try:
                users = [UserModel._default_manager.get(**{UserModel.EMAIL_FIELD: email})]
            except UserModel.DoesNotExist:
                users = None
        else:
            # Will check by the classic username field
            return super().authenticate(request, username, password, **kwargs)

        if not users:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
            return
        else:
            # Test whether any matched user has the provided password:
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
