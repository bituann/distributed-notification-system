from django.urls import path
from .views import signup_gateway, create_notification, health_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path("signup/", signup_gateway),
    path("notifications/", create_notification),
]
