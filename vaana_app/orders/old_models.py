# from random import choices
# from django.conf import settings
# from django.db import models
# from django.db.models.fields.related import ForeignKey
# from cores.models import TimestampedModel
# import uuid
# from carts.models import Cart, CartItem
# from addresses.models import Address
# from shippings.models import ShippingMethod

# class ShippingAddress(TimestampedModel):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     phone_number = models.CharField(max_length=255)
#     notes = models.TextField(blank=True, help_text="Tell us anything we should know when delivering your order.")
#     address = models.ForeignKey(Address, on_delete=models.CASCADE)

# class Order(TimestampedModel):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     number = models.CharField(max_length=128, db_index=True, unique=True, blank=True)
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart")
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         related_name='orders',
#         on_delete=models.SET_NULL
#     )
    
#     currency = models.CharField(max_length=12, default='EUR')
#     total_tax = models.DecimalField(decimal_places=2, max_digits=12)
#     shipping_tax = models.DecimalField(decimal_places=2, max_digits=12)
#     total_prices = models.DecimalField(decimal_places=2, max_digits=12)

#     INITIATED, CONFIRMED, SHIPPED, DELIVERED, CANCELED = (
#         "initiated", "confirmed", "shipped", "delivered", "canceled"
#     )
#     STATUS = [
#         (INITIATED, 'initiated'), 
#         (CONFIRMED, "confirmed"), 
#         (SHIPPED, "shipped"), 
#         (DELIVERED, "delivered"), 
#         (CANCELED, "canceled")
#         ]
#     shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)
    
#     shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)

#     # Use this field to indicate that an order is on hold / awaiting payment
#     status = models.CharField(max_length=100, default=INITIATED, choices=STATUS)

# class OrderItem(TimestampedModel):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     number = models.CharField(max_length=128, db_index=True, unique=True, blank=True)
#     seller = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         related_name='order_items',
#         on_delete=models.SET_NULL
#     )
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
#     cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
#     amount = models.DecimalField(decimal_places=2, max_digits=12)
#     currency = models.CharField(max_length=12, default='EUR')
#     shipping_tax = models.DecimalField(decimal_places=2, max_digits=12)
#     payment_intent_id = models.CharField(max_length=255, default=None, blank=True, null=True)
#     INITIATED, CONFIRMED, SHIPPED, DELIVERED, CANCELED = (
#         "initiated", "confirmed", "shipped", "delivered", "canceled"
#     )
#     STATUS = [
#         (INITIATED, 'initiated'), 
#         (CONFIRMED, "confirmed"), 
#         (SHIPPED, "shipped"), 
#         (DELIVERED, "delivered"), 
#         (CANCELED, "canceled")
#         ]
#     status = models.CharField(max_length=100, default=INITIATED, choices=STATUS)