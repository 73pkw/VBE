from django.conf import settings
from django.db import models
from cores.models import TimestampedModel
from orders.models import Order
import uuid

class PaymentModel(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.OneToOneField(Order, to_field='number', on_delete=models.CASCADE)
    method = models.CharField(max_length=255)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    currency = models.CharField(max_length=12, default='EUR')
    OPEN, DONE = (
        "open", 'done'
    )
    STATUS = [
        (OPEN, "open"),
        (DONE, "done")
    ]
    status = models.CharField(max_length=100, default=OPEN, choices=STATUS)

class CreditCard(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card_number = models.IntegerField()
    card_name = models.CharField(max_length=255)
    cvc = models.CharField(max_length=3)
    expiration_date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)

    def update(self, data):
        self.card_number = data['card_number']
        self.card_name = data['card_name']
        self.cvc = data['cvc']
        self.expiration_date = data['expiration_date']

        return self.save()

class BankAccount(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    bic = models.CharField(max_length=255)
    iban = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)

    def update(self, data):
        self.bic = data['bic']
        self.iban = data['iban']
        self.account_name = data['account_name']

        return self.save()
