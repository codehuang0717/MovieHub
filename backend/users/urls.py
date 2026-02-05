from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.user_profile, name="user_profile"),
    path(
        "profile/update/", views.UserProfileView.as_view(), name="user_profile_update"
    ),
    path("profile/avatar/upload/", views.upload_avatar, name="upload_avatar"),
    path("profile/avatar/remove/", views.remove_avatar, name="remove_avatar"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
