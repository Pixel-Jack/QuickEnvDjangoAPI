from django.contrib.auth import (
    get_user_model
)
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

UserModel = get_user_model()


class UserCreationSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.ModelField(model_field=UserModel._meta.get_field('password'),
                                                   label=_("Password confirmation"),
                                                   write_only=True)

    class Meta:
        model = UserModel
        fields = ('email', 'username', 'password', 'password_confirmation')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """
        Check that the two password are the same.
        """
        password1 = data.get('password')
        password2 = data.get('password_confirmation')
        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError(
                    {'password_mismatch_errors': _("The two password fields didn't match.")},
                    code='password_mismatch',
                )
        return data

    def create(self, validated_data):
        user = UserModel(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
