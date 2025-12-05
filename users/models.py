from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Почта")
    avatar = models.ImageField(upload_to="users/avatars", blank=True, null=True, verbose_name="Аватар")
    tg_chat_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram chat-id")
    # tg_nick = models.CharField(
    #     max_length=50,
    #     blank=True,
    #     null=True,
    #     verbose_name="Telegram-nick"
    # )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
