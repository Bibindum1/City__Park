import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render

from .models import Category, Dish, Order, OrderItem


def order_success(request, order_id):
    return render(request, "order_success.html", {"order_id": order_id})


def basket_view(request):
    cart = request.session.get("cart", {})

    total = sum(
        float(item["price"]) * item["quantity"]
        for item in cart.values()
    )

    return render(request, "basket/basket.html", {
        "cart": cart,
        "total": total,
    })

def favourites_view(request, dish_id):
    fav = request.session.get("fav", [])

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

    total_sum = sum((order.total for order in orders), Decimal("0.00"))
    avg_check = total_sum / orders.count() if orders.exists() else Decimal("0.00")

    return render(request, "profile.html", {
        "orders": orders,
        "total_sum": total_sum,
        "avg_check": avg_check,
    })


def checkout(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Метод POST обязателен."},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Некорректный JSON."},
            status=400,
        )

    cart = data.get("cart", [])

    if not isinstance(cart, list) or not cart:
        return JsonResponse({"status": "empty"})

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total=Decimal("0.00"),
    )

    total = Decimal("0.00")

    for item in cart:
        try:
            name = item["name"].strip()
            price = Decimal(str(item["price"]))
            quantity = int(item.get("quantity", 1))

            if quantity <= 0:
                continue
        except (KeyError, ValueError, InvalidOperation, TypeError):
            continue

        OrderItem.objects.create(
            order=order,
            name=name,
            price=price,
            quantity=quantity,
        )

        total += price * quantity

    if total == 0:
        order.delete()
        return JsonResponse({"status": "empty"})

    order.total = total
    order.save(update_fields=["total"])

    return JsonResponse({
        "status": "ok",
        "order_id": order.id,
    })

def add_to_cart(request, dish_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    dish = Dish.objects.get(id=dish_id)

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
    instance.order.update_total()