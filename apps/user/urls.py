from django.urls import path

from apps.user.contrib.drf import views

urlpatterns = [
    path('signup/', views.UserCreationView.as_view(), name='user-creation'),
]
