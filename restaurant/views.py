from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from catalog.models import Dish, Category


def menu_view(request):
    dishes = Dish.objects.select_related('category').all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        dishes = dishes.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    category = request.GET.get('category')
    if category and category != 'all':
        dishes = dishes.filter(category__slug=category)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        dishes = dishes.order_by('price')
    elif sort == 'price_desc':
        dishes = dishes.order_by('-price')
    elif sort == 'name':
        dishes = dishes.order_by('name')

    cart = request.session.get('cart', {})
    favs = request.session.get('favs', [])

    return render(request, 'menu.html', {
        'dishes': dishes,
        'categories': categories,
        'query': query,
        'category': category,
        'sort': sort,
        'cart': cart,
        'favs': favs,
    })


@require_POST
def add_to_cart(request, id):
    cart = request.session.get('cart', {})
    key = str(id)
    cart[key] = int(cart.get(key, 0)) + 1
    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
        "count": sum(int(v) for v in cart.values())
    })


@require_POST
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    key = str(id)

    if key in cart:
        cart[key] = int(cart.get(key, 0)) - 1
        if cart[key] <= 0:
            del cart[key]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
        "count": sum(int(v) for v in cart.values())
    })


def cart_view(request):
    cart = request.session.get('cart', {})
    ids = [int(i) for i in cart.keys() if str(i).isdigit()]

    dishes = Dish.objects.filter(id__in=ids).select_related('category')
    dish_map = {str(d.id): d for d in dishes}

    items = []
    total_count = 0
    total_sum = 0

    for dish_id, qty in cart.items():
        dish = dish_map.get(str(dish_id))
        if not dish:
            continue

        qty = int(qty)
        line_sum = qty * dish.price

        items.append({
            "dish": dish,
            "qty": qty,
            "sum": line_sum
        })

        total_count += qty
        total_sum += line_sum

    return render(request, 'basket.html', {
        'items': items,
        'total_count': total_count,
        'total_sum': total_sum,
    })


@require_POST
def toggle_fav(request, id):
    favs = request.session.get('favs', [])
    dish_id = int(id)

    if dish_id in favs:
        favs.remove(dish_id)
        state = "removed"
    else:
        favs.append(dish_id)
        state = "added"

    request.session['favs'] = favs
    request.session.modified = True

    return JsonResponse({
        "status": state,
        "favs": favs,
        "count": len(favs)
    })


def fav_view(request):
    favs = request.session.get('favs', [])
    dishes = Dish.objects.filter(id__in=favs)

    return render(request, "favorites.html", {
        "dishes": dishes
    })


@require_POST
def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    return JsonResponse({"status": "ok"})


def booking_view(request):
    return render(request, 'booking.html')


def about_view(request):
    return render(request, 'about.html')


def wine_view(request):
    return render(request, 'wine.html')


def contacts_view(request):
    return render(request, 'contacts.html')
