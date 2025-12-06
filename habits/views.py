from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from habits.models import Habit
from habits.paginations import CustomPagination
from habits.serializer import HabitSerializer
from users.permissions import IsHabitOwner


class HabitViewSet(ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = CustomPagination
    permission_classes = (IsHabitOwner, IsAuthenticated)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(public_flag=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserHabitListAPIView(ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = CustomPagination
    permission_classes = (IsHabitOwner, IsAuthenticated)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)
