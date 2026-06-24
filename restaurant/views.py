from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from catalog.models import Dish, Category
from restaurant.models import Booking


def menu_view(request):
    dishes = Dish.objects.select_related("category").all()
    categories = Category.objects.all()

    query = request.GET.get("q")
    if query:
        dishes = dishes.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    category = request.GET.get("category")
    if category and category != "all":
        dishes = dishes.filter(category__slug=category)

    sort = request.GET.get("sort")
    if sort == "price_asc":
        dishes = dishes.order_by("price")
    elif sort == "price_desc":
        dishes = dishes.order_by("-price")
    elif sort == "name":
        dishes = dishes.order_by("name")

    cart = request.session.get("cart", {})
    favs = request.session.get("favs", [])

    return render(request, "menu.html", {
        "dishes": dishes,
        "categories": categories,
        "query": query,
        "category": category,
        "sort": sort,
        "cart": cart,
        "favs": favs,
    })


@login_required
@require_POST
def add_to_cart(request, id):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}

    dish = get_object_or_404(Dish, id=id)
    key = str(id)

    current_qty = 0

    # поддержка старого формата (если вдруг int лежит)
    if isinstance(cart.get(key), dict):
        current_qty = cart[key].get("quantity", 0)
    elif isinstance(cart.get(key), int):
        current_qty = cart.get(key, 0)

    cart[key] = {
        "name": dish.name,
        "price": str(dish.price),
        "quantity": int(current_qty) + 1,
        "image": dish.image.url if dish.image else "",
    }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
        "count": sum(item.get("quantity", 0) for item in cart.values() if isinstance(item, dict))
    })


@require_POST
def remove_from_cart(request, id):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}

    key = str(id)

    if key in cart:
        if isinstance(cart[key], dict):
            qty = int(cart[key].get("quantity", 0)) - 1
        else:
            qty = int(cart[key]) - 1

        if qty <= 0:
            del cart[key]
        else:
            cart[key] = {
                "quantity": qty
            }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
        "count": sum(
            item.get("quantity", 0) if isinstance(item, dict) else int(item)
            for item in cart.values()
        )
    })


@login_required
def cart_view(request):
    cart = request.session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}
        request.session["cart"] = cart

    items = []
    total_count = 0
    total_sum = Decimal("0.00")

    for dish_id, data in cart.items():
        dish = get_object_or_404(Dish, id=int(dish_id))

        if isinstance(data, dict):
            qty = int(data.get("quantity", 0))
        else:
            qty = int(data)

        line_sum = dish.price * qty

        items.append({
            "dish": dish,
            "qty": qty,
            "sum": line_sum,
        })

        total_count += qty
        total_sum += line_sum

    return render(request, "basket/basket.html", {
        "items": items,
        "total_count": total_count,
        "total_sum": total_sum,
    })


@require_POST
def toggle_fav(request, id):
    favs = request.session.get("favs", [])
    dish_id = int(id)

    if dish_id in favs:
        favs.remove(dish_id)
        state = "removed"
    else:
        favs.append(dish_id)
        state = "added"

    request.session["favs"] = favs
    request.session.modified = True

    return JsonResponse({
        "status": state,
        "favs": favs,
        "count": len(favs)
    })


def fav_view(request):
    favs = request.session.get("favs", [])
    dishes = Dish.objects.filter(id__in=favs).select_related("category")

    return render(request, "basket/favourites.html", {
        "dishes": dishes
    })


@require_POST
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    return JsonResponse({"status": "ok"})


def booking_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip() or None
        booking_date = request.POST.get("booking_date")
        booking_time = request.POST.get("booking_time")
        guests = request.POST.get("guests", 1)
        comment = request.POST.get("comment", "").strip() or None

        booking = Booking.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            booking_date=booking_date,
            booking_time=booking_time,
            guests=int(guests),
            comment=comment,
        )
        return redirect("booking_success", booking_id=booking.id)

    return render(request, "booking.html")

def cart_count(request):
    cart = request.session.get("cart", {})
    count = sum(i.get("quantity", 0) for i in cart.values() if isinstance(i, dict))
    return JsonResponse({"count": count})


def fav_count(request):
    favs = request.session.get("favs", [])
    return JsonResponse({"count": len(favs)})


def booking_success(request, booking_id):
    return render(request, "order_success.html", {
        "order_id": booking_id
    })


def about_view(request):
    return render(request, "about.html")


def wine_view(request):
    return render(request, "wine.html")


def contacts_view(request):
    return render(request, "contacts.html")