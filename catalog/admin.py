from django.contrib import admin
from .models import Category, Dish, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "price", "quantity", "total_price")
    fields = ("name", "price", "quantity", "total_price")
    can_delete = False
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "weight", "calories", "is_available", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("category", "is_available", "created_at")
    search_fields = ("name", "description", "ingredients")
    list_editable = ("price", "is_available")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "total_time")
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "category", "description", "ingredients", "image")
        }),
        ("Характеристики", {
            "fields": ("price", "weight", "calories", "prep_time", "cooking_time", "total_time", "is_available")
        }),
        ("Служебная информация", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at")
        }),
    )
    ordering = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_display_links = ("id",)
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "user__email")
    list_editable = ("status",)
    readonly_fields = ("created_at", "total")
    inlines = (OrderItemInline,)
    ordering = ("-created_at",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_total()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "name", "price", "quantity", "total_price")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    readonly_fields = ("total_price",)
    ordering = ("order",)