from rest_framework.serializers import ModelSerializer

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
