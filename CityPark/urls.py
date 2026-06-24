from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

from catalog import views as catalog_views
from users.views import login_view, register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', catalog_views.index, name='index'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', login_view, name='login'),
    path('registration/', register_view, name='registration'),
    path('basket/', catalog_views.basket_view, name='basket'),
    path('favourites/', catalog_views.favourites_view, name='favourites'),
    path('checkout/', catalog_views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', catalog_views.order_success, name='order_success'),
    path('profile/', catalog_views.profile, name='profile'),
    path('add-to-cart/<int:dish_id>/', catalog_views.add_to_cart, name='add_to_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
