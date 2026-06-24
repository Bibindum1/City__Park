from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "full_name",
        "email",
        "phone",
        "is_staff",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "username",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "created_at",
    )

    search_fields = (
        "username",
        "full_name",
        "email",
        "phone",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        ("Основная информация", {
            "fields": (
                "username",
                "password",
            )
        }),

        ("Личная информация", {
            "fields": (
                "full_name",
                "first_name",
                "last_name",
                "email",
                "phone",
                "avatar",
                "address",
            )
        }),

        ("Права доступа", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Важные даты", {
            "fields": (
                "last_login",
                "date_joined",
                "created_at",
                "updated_at",
            )
        }),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "full_name",
                    "email",
                    "phone",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )