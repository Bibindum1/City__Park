from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from catalog.models import Dish


class RestaurantInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название ресторана")
    slogan = models.CharField(max_length=255, blank=True, verbose_name="Слоган")
    description = models.TextField(verbose_name="Описание")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    working_hours = models.CharField(max_length=100, verbose_name="Время работы")
    image = models.ImageField(upload_to="restaurant/", blank=True, null=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    seats = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Столик №{self.number}"


class Booking(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings"
    )

    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_NEW, "Новая"),
        (STATUS_CONFIRMED, "Подтверждена"),
        (STATUS_CANCELLED, "Отменена"),
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    booking_date = models.DateField()
    booking_time = models.TimeField()

    guests = models.PositiveSmallIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )

    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("booking_date", "booking_time")

    def __str__(self):
        return f"{self.full_name} — {self.booking_date} {self.booking_time}"

    def clean(self):
        exists = Booking.objects.filter(
            booking_date=self.booking_date,
            booking_time=self.booking_time
        ).exclude(pk=self.pk).exists()

        if exists:
            raise ValidationError("Это время уже занято")


class Review(models.Model):
    author = models.CharField(max_length=150)
    rating = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.author

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart({self.user})"

    def total_price(self):
        return sum(
            item.total_price() for item in self.items.all()
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "dish")

    def total_price(self):
        return self.dish.price * self.quantity