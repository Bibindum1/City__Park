from django.contrib import admin
from .models import RestaurantInfo, Booking, Table, Review


@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "email",
        "working_hours",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "address",
        "phone",
        "email",
    )

    fieldsets = (
        ("Основная информация", {
            "fields": (
                "name",
                "slogan",
                "description",
                "image",
            )
        }),
        ("Контактная информация", {
            "fields": (
                "address",
                "phone",
                "email",
                "working_hours",
            )
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "booking_date",
        "booking_time",
        "guests",
        "status",
        "created_at",
    )

    list_display_links = (
        "id",
        "full_name",
    )

    list_filter = (
        "status",
        "booking_date",
        "created_at",
    )

    search_fields = (
        "full_name",
        "phone",
        "email",
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        ("Контактные данные", {
            "fields": (
                "full_name",
                "phone",
                "email",
            )
        }),
        ("Бронирование", {
            "fields": (
                "booking_date",
                "booking_time",
                "guests",
                "status",
                "comment",
            )
        }),
        ("Служебная информация", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
            )
        }),
    )


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "seats",
        "is_active",
    )

    list_display_links = (
        "id",
        "number",
    )

    list_filter = (
        "is_active",
        "seats",
    )

    search_fields = (
        "number",
    )

    list_editable = (
        "is_active",
    )

    ordering = (
        "number",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "rating",
        "is_published",
        "created_at",
    )

    list_display_links = (
        "id",
        "author",
    )

    list_filter = (
        "rating",
        "is_published",
        "created_at",
    )

    search_fields = (
        "author",
        "text",
    )

    list_editable = (
        "is_published",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )