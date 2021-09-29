# from django.db import models
# from rest_framework import fields, serializers
# from .models import Order, OrderItem, ShippingAddress

# from addresses.serializers import AddressSerializer
# from shippings.serializers import ShippingMethodSerializer
# from carts.models import Cart
# from carts.serializers import CartDetailsSerializer, CartItemDetailsSerializer
# from products.serializers import ProductResponseSerializer

# class ShippingAddressSerializer(serializers.ModelSerializer):
#     address = AddressSerializer()

#     class Meta:
#         model = ShippingAddress
#         fields = [
#             "id",
#             "phone_number",
#             "notes",
#             "address",
#             "created_at",
#             "updated_at",
#         ]

# class OrderItemSerializer(serializers.ModelSerializer):
#     cart_item = CartItemDetailsSerializer()
#     class Meta:
#         model = OrderItem
#         fields = [
#             "id",
#             "number",
#             "order",
#             "payment_intent_id",
#             "cart_item",
#             "amount",
#             "status",
#             "currency",
#             "created_at",
#             "updated_at",
#         ]

# class OrderSerializer(serializers.ModelSerializer):
#     shipping_address = ShippingAddressSerializer()
#     shipping_method = ShippingMethodSerializer()
#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "number",
#             "cart",
#             "user",
#             "currency",
#             "total_tax",
#             "shipping_tax",
#             "total_prices",
#             "shipping_address",
#             "shipping_method",
#             "status",
#             "created_at",
#             "updated_at",
#         ]

#     def verify(self, fields):
#         for i in fields:
#             if i is None:
#                 raise serializers.ValidationError(
#                         i + 'field is required to initiate an order.'
#                     )


#     def validate(self, attrs):
#         shipping_address = attrs.get('shipping_address', None)
#         cart = attrs.get('cart', None)
#         currency = attrs.get('currency', None)
#         total_tax = attrs.get('total_tax', None)
#         shipping_tax = attrs.get('shipping_tax', None)
#         total_prices = attrs.get('total_prices', None)
#         shipping_method = attrs.get('shipping_method', None)

#         self.verify([cart, currency, total_tax, shipping_tax, total_prices, shipping_method, shipping_address])

#         if cart.status != Cart.OPEN:
#             raise serializers.ValidationError(
#                 'Cart not founded' 
#             )

#         return {
#             'shipping_address': shipping_address,
#             'cart': cart,
#             'currency': currency,
#             'total_tax': total_tax,
#             'shipping_tax': shipping_tax,
#             'total_prices': total_prices,
#             'shipping_method': shipping_method
#         }

# class OrderDetailsSerializer(serializers.ModelSerializer):
#     shipping_address = ShippingAddressSerializer()
#     shipping_method = ShippingMethodSerializer()
#     cart = CartDetailsSerializer()
#     order_items = OrderItemSerializer(many=True)
#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "number",
#             "cart",
#             "order_items",
#             "user",
#             "currency",
#             "total_tax",
#             "shipping_tax",
#             "total_prices",
#             "shipping_address",
#             "shipping_method",
#             "status",
#             "created_at",
#             "updated_at",
#         ]

# class OrderItemDetailsSerializer(serializers.ModelSerializer):
#     cart_item = CartItemDetailsSerializer()
#     order = OrderSerializer()
#     class Meta:
#         model = OrderItem
#         fields = [
#             "id",
#             "number",
#             "payment_intent_id",
#             "order",
#             "cart_item",
#             "amount",
#             "status",
#             "currency",
#             "created_at",
#             "updated_at",
#         ]
