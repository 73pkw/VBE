from addresses.models import Address
from django.db import models
from django.conf import settings
from cores.models import TimestampedModel
import uuid

class Store(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField()
    image = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def no_of_ratings(self):
        sum=0
        reviews = StoreReview.objects.filter(store=self)
        return len(reviews)

    # @property
    def avg_rating(self):
        sum=0
        reviews = StoreReview.objects.filter(store=self)
        for review in reviews:
            sum=sum+review.rating

        if len(reviews)>0:
            return sum/len(reviews)
        else:
            return 0
    
    rating = property(avg_rating)

class StoreReview(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    comment = models.TextField()
    rating = models.IntegerField()
    store = models.ForeignKey(Store, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.title
