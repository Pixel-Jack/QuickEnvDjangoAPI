from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"), max_length=254)


class AuthTokenSerializer(serializers.Serializer):
    login = serializers.CharField(label=_("Login"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, data):
        login = data.get('login')
        password = data.get('password')

        if login and password:
            user = authenticate(request=self.context.get('request'),
                                login=login, password=password)
        else:
            msg = _('Must include "login" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        # The authenticate call simply returns None for is_active=False
        # users. (Assuming the default ModelBackend authentication
        # backend.)
        if not user:
            msg = _('Unable to log in with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class SetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(label=_("New password"), trim_whitespace=False)
    new_password2 = serializers.CharField(label=_("New password confirmation"), trim_whitespace=False)

    def validate(self, data):
        """
        Check that the two password are the same.
        """
        password1 = data.get('new_password1')
        password2 = data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError(
                    {'password_mismatch_errors': _("The two password fields didn't match.")},
                    code='password_mismatch',
                )
        return data


class OldPasswordSerializer(serializers.Serializer):
    """
    A serializer that lets a user change their password by entering their old password.
    """
    old_password = serializers.CharField(label=_("Old password"), trim_whitespace=False)

    def __init__(self, user, *args, **kwargs):
        assert isinstance(user, get_user_model())
        self.user = user
        super(OldPasswordSerializer, self).__init__(*args, **kwargs)

    def validate_old_password(self, data):
        """
        Validate that the old_password field is correct.
        """
        if not self.user.check_password(data):
            raise serializers.ValidationError(
                {'password_incorrect': _("Your old password was entered incorrectly. Please enter it again.")},
                code='password_incorrect',
            )
        return data


class PasswordChangeSerializer(OldPasswordSerializer, SetPasswordSerializer):
    """
    A serializer that lets a user change their password by entering their old password.
    """

    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeSerializer, self).__init__(user=user, *args, **kwargs)
