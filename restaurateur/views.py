from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.db.models import DecimalField, F, Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance
from requests.exceptions import HTTPError

from foodcartapp.models import Order, Product, Restaurant
from star_burger.settings import YANDEX_GEOCODER_API_KEY

from .utils import fetch_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = [
        {'id': order.id,
         'status': order.get_status_display(),
         'firstname': order.firstname,
         'phonenumber': order.phonenumber,
         'lastname': order.lastname,
         'address': order.address,
         'comment': order.comment,
         'payment_method': order.get_payment_method_display(),
         'restaurants': sorted(_get_order_restaurants_with_coords(order),
                               key=lambda restaurant: restaurant['distance']
                               ),
         'total_amount': order.total_amount,

         }

        for order in (Order.objects
                      .prefetch_related('items__product__menu_items')
                      .order_by('-registered_at')
                      .get_total_amount()
                      )

    ]

    return render(request, template_name='order_items.html', context={
        'orders': orders,
    })


def _get_order_restaurants(order) -> set:
    restaurants = set()

    for item in order.items.all():
        for menu_item in item.product.menu_items.filter(availability=True):
            restaurants.add(menu_item.restaurant)

    return restaurants


def _get_order_restaurants_with_coords(order) -> list:
    restaurants = []

    for restaurant in _get_order_restaurants(order):
        try:
            distance_ = _get_distance(order.address, restaurant.address)
        except (IndexError, HTTPError):
            continue
        restaurants.append({'name': restaurant.name,
                            'distance': distance_})

    return restaurants


def _get_distance(place, restaurant):
    place_coords, restaurant_coords = map(_get_coordinates, [place, restaurant])
    distance_ = distance.distance(place_coords, restaurant_coords)

    return distance_.km


def _get_coordinates(place):
    coords = cache.get(place)

    if coords is None:
        coords = fetch_coordinates(YANDEX_GEOCODER_API_KEY, place)
        cache.set(place, coords, 60 * 30)

    return coords
