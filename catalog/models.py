from decimal import Decimal

import cart
from django.db import models, IntegrityError, transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=False)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            if not base:
                base = f"category-{uuid.uuid4().hex[:6]}"

            slug = base
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Dish(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="dishes")
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="dishes/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.PositiveIntegerField(default=100)
    calories = models.PositiveIntegerField(default=0)
    prep_time = models.PositiveIntegerField(default=5)
    cooking_time = models.PositiveIntegerField(default=15)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or f"dish-{uuid.uuid4().hex[:8]}"
            slug = base
            counter = 1
            while Dish.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def total_time(self):
        return self.prep_time + self.cooking_time


class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_PAID = "paid"
    STATUS_PREPARING = "preparing"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_NEW, "Новый"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_PREPARING, "Готовится"),
        (STATUS_DONE, "Выполнен"),
        (STATUS_CANCELLED, "Отменён"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.pk}"

    def update_total(self, save=True):
        total = sum(
            Decimal(str(item["price"])) * Decimal(item["quantity"])
            for item in cart.values()
        )
        self.total = total
        if save:
            self.save(update_fields=["total"])
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return self.name

    @property
    def total_price(self):
        return self.price * self.quantity