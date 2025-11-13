from django.urls import path
from .views import create_user, get_user

urlpatterns = [
    path("", create_user),  # POST /api/v1/users/
    path("<uuid:user_id>/", get_user),  # GET /api/v1/users/{uuid}/
]
