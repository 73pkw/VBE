from django.conf import settings
from django.db import models
from django.db.models.fields.related import ForeignKey
from cores.models import TimestampedModel
import uuid
from carts.models import Cart, CartItem
from shippings.models import Address, Shipment
from payments.models import PaymentMethod

class Order(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart")
    total_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='orders',
        on_delete=models.SET_NULL
    )

class OrderItem(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=128, db_index=True, unique=True, blank=True, null=True)
    shipping_address = models.ForeignKey(Address, blank=True, null=True, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, null=True, blank=True, on_delete=models.CASCADE)
    shipping_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    total_prices = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='order_items',
        on_delete=models.SET_NULL
    )
    cart_item = models.ForeignKey(CartItem, blank=True, null=True, on_delete=models.CASCADE, default=None)
    INITIATED, CONFIRMED, SHIPPED, DELIVERED, CANCELED = (
        "initiated", "confirmed", "shipped", "delivered", "canceled"
    )
    STATUS = [
        (INITIATED, 'initiated'), 
        (CONFIRMED, "confirmed"), 
        (SHIPPED, "shipped"), 
        (DELIVERED, "delivered"), 
        (CANCELED, "canceled")
        ]
    status = models.CharField(max_length=100, default=INITIATED, choices=STATUS, blank=True)

    def update(self, data):
        self.shipping_address = Address.objects.get(id=data['shipping_address']) if 'shipping_address' in data else self.shipping_address
        self.shipping_tax = data['shipping_tax'] if 'shipping_tax' in data else self.shipping_tax
        self.payment_method = data['payment_method'] if 'payment_method' in data else self.payment_method

        return self.save()
