from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = request.data

    if not order_data:
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    for key in ['address', 'firstname', 'lastname', 'phonenumber']:
        if key not in order_data:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(order_data[key], str):
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        if not order_data[key]:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    products = order_data.get('products')

    if not isinstance(products, list):
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    if not products:
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    for item in products:
        if not isinstance(item['product'], int):
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        get_object_or_404(Product, pk=item['product'])

        if not isinstance(item['quantity'], int):
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
        if item['quantity'] < 1:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    order, _ = Order.objects.update_or_create(address=order_data['address'],
                                              firstname=order_data['firstname'],
                                              lastname=order_data['lastname'],
                                              phone_number=order_data['phonenumber'],
                                              )

    for item in products:
        order_item, _ = OrderItem.objects.update_or_create(order=order,
                                                           product=get_object_or_404(Product, pk=item['product']),
                                                           quantity=item['quantity'],
                                                           )
    return Response(request.data, status=status.HTTP_201_CREATED)
