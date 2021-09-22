from django.db.models import fields
from rest_framework import serializers
from .models import Parcel, Shipment, ShippingMethod, Address, Transaction 


class ShippoAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "object_id",
            "company",
            "name",
            "state",
            "street1",
            "city",
            "zip_code",
            "country",
            "phone",
            "email",
            "user"
        ]
class ShippoParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = [
            "id",
            "object_id",
            "parcel_length",
            "parcel_width",
            "parcel_weight",
            "parcel_height",
            "distance_unit",
            "mass_unit"
        ]

class ShippoShipmentSerializer(serializers.ModelSerializer):
    address_from = ShippoAddressSerializer()
    address_to = ShippoAddressSerializer()
    parcels = ShippoParcelSerializer(many=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "object_id",
            "address_from",
            "address_to",
            "parcels"
        ]

    def createAddress(self, data):
        return Address.objects.create(
            name=data['name'],
            state=data['state'],
            street1=data['street1'],
            city=data['city'],
            zip_code=data['zip_code'],
            country=data['country'],
            phone=data['phone'],
            email=data['email'],
            company=data['name'] if 'company' in data else None,
        )

    def createParcel(self, data):
        return Parcel.objects.create(
            parcel_length=data['parcel_length'],
            parcel_width=data['parcel_width'],
            parcel_weight=data['parcel_weight'],
            parcel_height=data['parcel_height'],
            distance_unit=data['distance_unit'],
            mass_unit=data['mass_unit'],
        )
        
    def create(self, validated_data):
        shipment = Shipment()
        shipment.address_from = self.createAddress(validated_data['address_from']) 
        shipment.address_to = self.createAddress(validated_data['address_to'])
        shipment.save() 
        for i in validated_data['parcels']:
            shipment.parcels.add(self.createParcel(i))
        
        return ShippoShipmentSerializer(shipment).data

class ShippoTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "object_id",
            "shipment",
            "carrier_account",
            "servicelevel_token"
        ]

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = [
            "id",
            "name",
            "price",
            "currency"
        ]