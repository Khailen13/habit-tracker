from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users import views

app_name = UsersConfig.name

# router = SimpleRouter()
# router.register(r"payments", PaymentViewSet)

urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("", views.UserListAPIView.as_view(), name="user_list"),
    path("<int:pk>/", views.UserRetrieveAPIView.as_view(), name="user_retrieve"),
    path("<int:pk>/update/", views.UserUpdateAPIView.as_view(), name="user_update"),
    path("<int:pk>/delete/", views.UserDestroyAPIView.as_view(), name="user_delete"),
]

# urlpatterns += router.urls
