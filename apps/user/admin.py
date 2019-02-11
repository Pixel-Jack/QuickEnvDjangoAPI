from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminOld

from apps.user.forms import UserChangeForm, UserCreationForm
from apps.user.models import User


class UserAdmin(UserAdminOld):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['email', 'username', ]


admin.site.register(User, UserAdmin)
