from django.contrib.auth.forms import UserChangeForm as UserChangeFormOld
from django.contrib.auth.forms import UserCreationForm as UserCreationFormOld

from apps.user.models import User


class UserCreationForm(UserCreationFormOld):
    class Meta(UserCreationFormOld):
        model = User
        fields = ('username', 'email')


class UserChangeForm(UserChangeFormOld):
    class Meta:
        model = User
        fields = ('username', 'email')
