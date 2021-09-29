from django.db.models import fields
from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "country",
            "state",
            "street",
            "zipcode",
            'phone',
            'city'
        ]
