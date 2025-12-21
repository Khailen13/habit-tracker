from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(email="user1@mail.ru", tg_chat_id="some_id1")
        self.user2 = User.objects.create(email="user2@mail.ru", tg_chat_id="some_id2")
        self.client.force_authenticate(user=self.user1)
        self.habit11 = Habit.objects.create(
            user=self.user1,
            place="Место 1-1",
            time="16:00:00",
            action="Приятная привычка 1-1",
            is_pleasant=True,
            related_habit=None,
            award=None,
            duration=timedelta(seconds=120),
            periodicity=None,
            public_flag=True,
        )
        self.habit21 = Habit.objects.create(
            user=self.user2,
            place="Место 2-1",
            time="16:00:00",
            action="Приятная привычка 2-1",
            is_pleasant=True,
            related_habit=None,
            award=None,
            duration=timedelta(seconds=100),
            periodicity=None,
            public_flag=True,
        )

    def test_habit_list(self):
        url = reverse("habits:habit-list")
        response = self.client.get(url)
        response_json = response.json()
        expected_result_count = Habit.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json.get("results")), expected_result_count)

    def test_user_habit_list(self):
        url = reverse("habits:user-habit-list")
        response = self.client.get(url)
        response_json = response.json()
        expected_result_count = Habit.objects.filter(user=self.user1).count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json.get("results")), expected_result_count)

    def test_own_habit_detail(self):
        url = reverse("habits:habit-detail", args=(self.habit11.pk,))
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("user"), self.user1.pk)
        self.assertEqual(response_json.get("place"), self.habit11.place)

    def test_foreign_habit_detail(self):
        url = reverse("habits:habit-detail", args=(self.habit21.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_habit_update(self):
        url = reverse("habits:habit-detail", args=(self.habit11.pk,))
        data = {"place": "Место 1-55"}
        response = self.client.patch(url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("name"), data.get("name"))

    def test_foreign_habit_update(self):
        url = reverse("habits:habit-detail", args=(self.habit21.pk,))
        data = {"place": "Место 2-55"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_habit_delete(self):
        url = reverse("habits:habit-detail", args=(self.habit11.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.all().count(), 1)

    def test_foreign_habit_delete(self):
        url = reverse("habits:habit-detail", args=(self.habit21.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_create1(self):
        """Проверка успешного создания привычки."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=120),
            "periodicity": 1,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.all().count(), 3)

    def test_habit_create2(self):
        """Проверка вызова ошибки при создании полезной привычки без периодичности."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": None,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create3(self):
        """Проверка вызова ошибки при создании полезной привычки с периодичностью."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Приятная привычка 1-2",
            "is_pleasant": True,
            "related_habit": None,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 2,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create4(self):
        """Проверка вызова ошибки при создании полезной привычки с нулевой периодичностью."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 0,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create5(self):
        """Проверка вызова ошибки при создании полезной привычки с периодичностью больше 7 дней."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create6(self):
        """Проверка вызова ошибки при создании привычки с длительностью больше 120 сек."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create7(self):
        """Проверка вызова ошибки при создании привычки с длительностью больше 120 сек."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create8(self):
        """Проверка: у приятной привычки не может быть вознаграждения."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Приятная привычка 1-2",
            "is_pleasant": True,
            "related_habit": None,
            "award": "Вознаграждение",
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create9(self):
        """Проверка: у приятной привычки не может быть связанного ключа."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Приятная привычка 1-2",
            "is_pleasant": True,
            "related_habit": self.habit11.pk,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create10(self):
        """Проверка: у полезной привычки должно быть либо вознаграждение, либо связанная причина."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": None,
            "award": None,
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_create11(self):
        """Проверка: у полезной привычки не может быть одновременно и вознаграждения и связанной причины."""

        url = reverse("habits:habit-list")
        data = {
            "place": "Место 1-2",
            "time": "12:00:00",
            "action": "Полезная привычка 1-2",
            "is_pleasant": False,
            "related_habit": self.habit11.pk,
            "award": "Вознаграждение 1-2",
            "duration": timedelta(seconds=130),
            "periodicity": 8,
            "public_flag": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
