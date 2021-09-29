from django.db import models
from cores.models import TimestampedModel
import uuid

class Address(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)
    phone = models.CharField(max_length=255, default=None, null=True, blank=True)
