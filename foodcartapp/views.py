from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product
from .serializers import OrderItemSerializer, OrderSerializer


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
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.is_valid(raise_exception=True)

    items_serializer = OrderItemSerializer(data=request.data.get('products', []), many=True)
    items_serializer.is_valid(raise_exception=True)

    validated_items = items_serializer.validated_data
    if not validated_items:
        return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    validated_order = order_serializer.validated_data
    order = Order.objects.create(address=validated_order['address'],
                                 firstname=validated_order['firstname'],
                                 lastname=validated_order['lastname'],
                                 phonenumber=validated_order['phonenumber'],
                                 )

    for order_item in validated_items:
        OrderItem.objects.get_or_create(order=order,
                                        product=order_item['product'],
                                        quantity=order_item['quantity'],
                                        price=order_item['product'].price
                                        )

    return Response(request.data, status=status.HTTP_201_CREATED)
