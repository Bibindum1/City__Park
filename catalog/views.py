import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction

from restaurant.models import Booking
from .models import Category, Dish, Order, OrderItem


def order_success(request, order_id):
    return render(request, "order_success.html", {"order_id": order_id})


def basket_view(request):
    cart = request.session.get("cart", {})

    total = sum(
        Decimal(str(item["price"])) * Decimal(item["quantity"])
        for item in cart.values()
    )

    return render(request, "basket/basket.html", {
        "cart": cart,
        "total": total,
    })


def favourites_view(request, dish_id):
    fav = request.session.get("fav", [])
    dish_id = int(dish_id)

    if dish_id in fav:
        fav.remove(dish_id)
    else:
        fav.append(dish_id)

    request.session["fav"] = fav
    request.session.modified = True

    return JsonResponse({"status": "ok"})


def index(request):
    dishes = (
        Dish.objects
        .filter(is_available=True)
        .select_related("category")
    )
    categories = Category.objects.all()

    return render(request, "index.html", {
        "dishes": dishes,
        "categories": categories,
    })


@login_required
def profile(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    orders_count = orders.count()
    total_sum = sum((order.total for order in orders), Decimal("0.00"))
    avg_check = total_sum / orders_count if orders_count else Decimal("0.00")

    paid_orders_count = orders.filter(status__in=["PAID", "COMPLETED", "DONE"]).count()
    pending_orders_count = orders.filter(status__in=["PENDING", "NEW", "CREATED"]).count()
    cancelled_orders_count = orders.filter(status__in=["CANCELLED", "CANCELED"]).count()

    bookings = (
        Booking.objects
        .filter(user=request.user)
        .order_by("-booking_date", "-booking_time")
    )

    return render(request, "profile.html", {
        "orders": orders,
        "orders_count": orders_count,
        "total_sum": total_sum,
        "avg_check": round(avg_check, 2),

        "paid_orders_count": paid_orders_count,
        "pending_orders_count": pending_orders_count,
        "cancelled_orders_count": cancelled_orders_count,

        "bookings": bookings,
        "bookings_count": bookings.count(),
    })

@login_required
def checkout(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Метод POST обязателен."
        }, status=405)

    try:
        if "application/json" in request.content_type:
            data = json.loads(request.body.decode("utf-8") or "{}")
        else:
            data = request.POST

        cart = request.session.get("cart", {})

        if not isinstance(cart, dict) or not cart:
            return JsonResponse({
                "status": "error",
                "message": "Корзина пуста."
            }, status=400)

        name = str(data.get("name", "")).strip()
        phone = str(data.get("phone", "")).strip()
        address = str(data.get("address", "")).strip()
        delivery_time = str(data.get("delivery_time", "")).strip()
        payment_method = str(data.get("payment_method", "")).strip()
        comment = str(data.get("comment", "")).strip()

        if not name or not phone or not address:
            return JsonResponse({
                "status": "error",
                "message": "Заполните имя, телефон и адрес."
            }, status=400)

        order_field_names = {field.name for field in Order._meta.fields}

        order_kwargs = {
            "total": Decimal("0.00"),
        }

        if "user" in order_field_names:
            order_kwargs["user"] = request.user

        if "name" in order_field_names:
            order_kwargs["name"] = name
        if "customer_name" in order_field_names:
            order_kwargs["customer_name"] = name
        if "full_name" in order_field_names:
            order_kwargs["full_name"] = name

        if "phone" in order_field_names:
            order_kwargs["phone"] = phone

        if "address" in order_field_names:
            order_kwargs["address"] = address

        if "delivery_time" in order_field_names:
            order_kwargs["delivery_time"] = delivery_time

        if "payment_method" in order_field_names:
            order_kwargs["payment_method"] = payment_method

        if "comment" in order_field_names:
            order_kwargs["comment"] = comment

        if "status" in order_field_names:
            order_kwargs["status"] = "PENDING"

        order_item_field_names = {field.name for field in OrderItem._meta.fields}

        with transaction.atomic():
            order = Order.objects.create(**order_kwargs)

            total = Decimal("0.00")

            for dish_id, item in cart.items():
                try:
                    dish = Dish.objects.get(id=int(dish_id))
                    quantity = int(item.get("quantity", 1))
                except (Dish.DoesNotExist, ValueError, TypeError, AttributeError):
                    continue

                if quantity <= 0:
                    continue

                price = dish.price
                total += price * quantity

                item_kwargs = {
                    "order": order,
                    "quantity": quantity,
                }

                if "dish" in order_item_field_names:
                    item_kwargs["dish"] = dish

                if "name" in order_item_field_names:
                    item_kwargs["name"] = dish.name

                if "price" in order_item_field_names:
                    item_kwargs["price"] = price

                if "total" in order_item_field_names:
                    item_kwargs["total"] = price * quantity

                OrderItem.objects.create(**item_kwargs)

            if total <= 0:
                return JsonResponse({
                    "status": "error",
                    "message": "Не удалось оформить заказ: корзина пуста."
                }, status=400)

            order.total = total
            order.save(update_fields=["total"])

        request.session["cart"] = {}
        request.session.modified = True

        return JsonResponse({
            "status": "ok",
            "message": "Заказ успешно оформлен.",
            "order_id": order.id,
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Ошибка сервера: {type(e).__name__}: {str(e)}"
        }, status=500)

def add_to_cart(request, dish_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    dish = get_object_or_404(Dish, id=dish_id)

    cart = request.session.get("cart", {})

    if str(dish_id) in cart:
        cart[str(dish_id)]["quantity"] += 1
    else:
        cart[str(dish_id)] = {
            "name": dish.name,
            "price": str(dish.price),
            "quantity": 1,
        }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({"status": "ok", "cart": cart})


@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    if hasattr(instance.order, "update_total"):
        try:
            instance.order.update_total()
        except Exception:
            pass