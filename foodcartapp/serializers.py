from rest_framework.serializers import ModelSerializer

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        exclude = ['order']


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'status',
            'comment',
            'registered_at',
            'called_at',
            'delivered_at',
            'payment_method'
        ]
