from django.urls import path, include

urlpatterns = [
    path('', include('apps.first_app.contrib.drf.urls')),
]