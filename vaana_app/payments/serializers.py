from rest_framework import fields, serializers
from .models import BankAccount, CreditCard, Payment, PaymentMethod, PaymentModel

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "method",
            "amount",
            "currency",
            "created_at",
            'user'
        ]


class StripePaymentIntentConfirmSerializer(serializers.Serializer):
    order = serializers.CharField(max_length=255)

    def validate(self, attrs):
        order = attrs.get('order', None)
        
        if order is None:
            raise serializers.ValidationError(
                'order field is required'
            )

        return {
            'order' : order
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

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'method',
            'card',
            'bank_account',
            'user'
        ]
