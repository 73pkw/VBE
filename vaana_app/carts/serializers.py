from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductResponseSerializer

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "created_at",
            "updated_at",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = [
            "id",
            "owner",
            "status",
            "merged_date",
            "items",
            "created_at",
            "updated_at",
        ]

class CartItemDetailsSerializer(serializers.ModelSerializer):
    product = ProductResponseSerializer()
    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "created_at",
            "updated_at",
        ]

class CartDetailsSerializer(serializers.ModelSerializer):
    items = CartItemDetailsSerializer(many=True)
    class Meta:
        model = Cart
        fields = [
            "id",
            "owner",
            "status",
            "merged_date",
            "items",
            "created_at",
            "updated_at",
        ]
