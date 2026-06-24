from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    full_name = models.CharField(
        max_length=150,
        verbose_name="ФИО"
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Адрес доставки"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username