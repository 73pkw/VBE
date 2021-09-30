from django.conf import settings
from django.db import models

from cores.models import TimestampedModel
import uuid

class Address(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_id = models.CharField(max_length=255, blank=True, default=None, null=True)
    company = models.CharField(max_length=255, blank=True, null=True, default=None)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    street1 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='shipping_address')

    def update(self, data):
        self.company = data['company'] if 'company' in data else None
        self.name = data['name']
        self.state = data['state']
        self.street1 = data['street1']
        self.city = data['city']
        self.zip_code = data['zip_code']
        self.country = data['country']
        self.phone = data['phone']
        self.email = data['email']

        return self.save()

class Parcel(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_id = models.CharField(max_length=255, blank=True, default=None, null=True)
    parcel_length = models.DecimalField(max_digits=12, decimal_places=3)
    parcel_width = models.DecimalField(max_digits=12, decimal_places=3)
    parcel_weight = models.DecimalField(max_digits=12, decimal_places=3)
    parcel_height = models.DecimalField(max_digits=12, decimal_places=3)
    distance_unit = models.CharField(max_length=255)
    mass_unit = models.CharField(max_length=255)

class Shipment(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_id = models.CharField(max_length=255, blank=True, default=None, null=True)
    address_from = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='address_from')
    address_to = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='address_to')
    parcels = models.ManyToManyField(Parcel)
    carrier_account = models.CharField(max_length=255, null=True, blank=True)
    servicelevel_token = models.CharField(max_length=255, null=True, blank=True)
    rate = models.CharField(max_length=255, blank=True, null=True, default=None)

    def update(self, data):
        self.carrier_account = data['carrier_account'] if 'carrier_account' in data else self.carrier_account
        self.servicelevel_token = data['servicelevel_token'] if 'servicelevel_token' in data else self.servicelevel_token
        self.rate = data['rate'] if 'rate' in data else self.rate
        return self.save()
        

class Transaction(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_id = models.CharField(max_length=255, blank=True, default=None, null=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    carrier_account = models.CharField(max_length=255)
    servicelevel_token = models.CharField(max_length=255)

class ShippingMethod(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=3)
    currency = models.CharField(max_length=255, default='EUR')
