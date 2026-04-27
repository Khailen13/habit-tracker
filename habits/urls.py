from django.urls import path
from rest_framework.routers import SimpleRouter

from habits.apps import HabitsConfig
from habits.views import HabitViewSet, UserHabitListAPIView

app_name = HabitsConfig.name

router = SimpleRouter()
router.register("", HabitViewSet)

urlpatterns = [
    path("user/", UserHabitListAPIView.as_view(), name="user-habit-list"),
]

urlpatterns += router.urls
