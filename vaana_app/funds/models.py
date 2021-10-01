from django.db import models
from cores.models import TimestampedModel
import uuid
from django.conf import settings
from products.models import Product
from payments.models import Payment
from wallets.models import Wallet

class Fund(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    currency = models.CharField(max_length=12, default='EUR')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="funds")
    transaction_id = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


    COLLECTED, REFUNDED, TRANSFERED, READY = (
        "collected", "refunded", "transfered", "ready"
    )

    STATUS = [
        (COLLECTED, "collected"),
        (REFUNDED, "refunded"),
        (TRANSFERED, "trensfered"),
        (READY, "ready")
    ]

    status = models.CharField(max_length=100, default=COLLECTED, choices=STATUS)

