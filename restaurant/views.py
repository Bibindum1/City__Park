from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse

from catalog.models import Dish, Category


# ---------------- MENU ----------------

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


# ---------------- CART ----------------

def add_to_cart(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    cart = request.session.get('cart', {})

    id = str(id)

    if id in cart:
        cart[id] += 1
    else:
        cart[id] = 1

    request.session['cart'] = cart
    request.session.modified = True= cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
        "count": sum(cart.values())
    })


def remove_from_cart(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    cart = request.session.get('cart', {})
    id = str(id)

    if id in cart:
        cart[id] -= 1
        if cart[id] <= 0:
            del cart[id]

    request.session['cart'] = cart
    request.session.modified = True= cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
        "count": sum(cart.values())
    })


def cart_view(request):
    cart = request.session.get('cart', {})
    ids = cart.keys()

    dishes = Dish.objects.filter(id__in=ids)

    items = []
    total_count = 0

    for dish in dishes:
        qty = cart.get(str(dish.id), 0)
        total_count += qty
        items.append({
            "dish": dish,
            "qty": qty,
            "sum": qty * dish.price
        })

    return render(request, "cart.html", {
        "items": items,
        "total_count": total_count
    })


# ---------------- FAVORITES ----------------

def toggle_fav(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    favs = request.session.get('favs', [])
    id = int(id)

    if id in favs:
        favs.remove(id)
        state = "removed"
    else:
        favs.append(id)
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


# ---------------- STATIC ----------------

def booking_view(request):
    return render(request, 'booking.html')

def about_view(request):
    return render(request, 'about.html')

def wine_view(request):
    return render(request, 'wine.html')

def contacts_view(request):
    return render(request, 'contacts.html')