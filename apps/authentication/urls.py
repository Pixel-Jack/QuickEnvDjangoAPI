from django.urls import path

from apps.authentication.contrib.drf import views

urlpatterns = [
    path('obtain-token/', views.ObtainAuthToken.as_view(), name='obtain-token'),
    path('refresh-token/', views.RefreshAuthToken.as_view(), name='refresh-token'),
    path('delete-token/', views.DeleteAuthToken.as_view(), name='delete-token'),


    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('reset-password/', views.PasswordResetView.as_view(), name='reset-password'),
    path('reset/<pk>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

]
