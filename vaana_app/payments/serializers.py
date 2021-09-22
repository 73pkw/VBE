from rest_framework import fields, serializers
from .models import BankAccount, CreditCard, PaymentModel

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = [
            "id",
            "order_number",
            "method",
            "amount",
            "currency",
            "created_at"
        ]

class StripePaymentIntentConfirmSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=255)

    def validate(self, attrs):
        order_number = attrs.get('order_number', None)
        
        if order_number is None:
            raise serializers.ValidationError(
                'order_number field is required'
            )

        return {
            'order_number' : order_number
        }

class BraintreeTransactionSerializer(serializers.Serializer):
    nonce = serializers.CharField(max_length=255)
    device_data = serializers.CharField(max_length=255, required=False, default=None)
    payment = PaymentSerializer()

    class Meta:
        fields = [
            "nonce",
            "device_data",
            "payment"
        ]

class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = [
            'id',
            'card_number',
            'card_name',
            'cvc',
            'expiration_date',
            'user'
        ]

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id',
            'bic',
            'iban',
            'account_name',
            'user',
        ]
