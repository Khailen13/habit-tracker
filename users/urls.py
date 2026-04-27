from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name


urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("", views.UserListAPIView.as_view(), name="user_list"),
    path("<int:pk>/", views.UserRetrieveAPIView.as_view(), name="user_retrieve"),
    path("<int:pk>/update/", views.UserUpdateAPIView.as_view(), name="user_update"),
    path("<int:pk>/delete/", views.UserDestroyAPIView.as_view(), name="user_delete"),
]
