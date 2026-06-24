from django.urls import path
from . import views

urlpatterns = [
    path("menu/", views.menu_view, name="menu"),
    path("booking/", views.booking_view, name="booking"),
    path("booking/success/<int:booking_id>/", views.booking_success, name="booking_success"),
    path("about/", views.about_view, name="about"),
    path("wine/", views.wine_view, name="wine"),
    path("contacts/", views.contacts_view, name="contacts"),

    path("cart/add/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),

    path("fav/toggle/<int:id>/", views.toggle_fav, name="toggle_fav"),
    path("fav/", views.fav_view, name="fav"),
]