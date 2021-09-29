from .models import Order, OrderItem
from rest_framework import serializers
from carts.serializers import CartItemSerializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'cart',
            'user',
            'total_tax'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    cart_item = CartItemSerializer()
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'number',
            'shipping_address',
            'shipping_tax',
            'total_prices',
            'payment_method',
            'seller',
            'cart_item',
            'status',
            'shipment',
            "created_at",
            "updated_at",
        ]

class OrderDetailsSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = [
            'id',
            'cart',
            'total_tax',
            "order_items",
        ]
