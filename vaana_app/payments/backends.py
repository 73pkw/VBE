import braintree
from django.conf import settings
import stripe
from .models import Payment, PaymentModel
from cores.utils import *
from funds.backends import FundController
from wallets.backends import WalletController
from orders.models import Order, OrderItem
from orders.serializers import OrderDetailsSerializer

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY
    )
)

stripe.api_key = settings.STRIPE_SECRET_KEY

class BraintreeAPI(object):
    def get_client_token(self):
        return gateway.client_token.generate()

    def transaction_sale(self, data, user):
        return gateway.transaction.sale({
            "amount": data['amount'],
            "payment_method_nonce": data['nonce'],
            "device_data": data['device_data'] if 'device_data' in data else None,
            "customer":{
                "email": user.email,
            },
            "options": {
                "submit_for_settlement": True
            }
        })

    def getTransactionObject(self, transaction):
        return {
            'id': transaction.id,
            'graphql_id': transaction.graphql_id,
            'amount': transaction.amount,
            'currency_iso_code': transaction.currency_iso_code,
            'payment_instrument_type': transaction.payment_instrument_type,
            'processor_response_text': transaction.processor_response_text,
            'processor_settlement_response_code': transaction.processor_settlement_response_code,
            'processor_settlement_response_text': transaction.processor_settlement_response_text,
            'settlement_batch_id': transaction.settlement_batch_id,
            'status': transaction.status,
        }

class StripeAPI(object):

    def getPaymentIntent(self, user, data, order):
        customer = stripe.Customer.create(
                name=user.username,
                email=user.email
            )
        intent = stripe.PaymentIntent.create(
            payment_method_types=[data['method']],
            amount = data['amount'] * 100,
            currency = data['currency'],
            customer=customer.id,
            metadata={
                "order": order.id
            },
            receipt_email=user.email
        )

        return intent

    def retrievePaymentIntent(self, payment_intent_id):

        return stripe.PaymentIntent.retrieve(payment_intent_id)

class PaymentBackend(object):
    def create(self, data):
        return Payment.objects.create(
            order=data['order'],
            method=data['method'],
            amount=data['amount'],
            currency=data['currency'],
            status=data['status'] if 'status' in data else PaymentModel.OPEN
        )
    
    def updateOrderItemStatus(self, order, status, payment_intent_id):
        items = OrderItem.objects.filter(order=order)
        for item in items:
            item.transaction_id = payment_intent_id
            item.status = status
            item.save()

    def updateProductsQuantity(self, order, payment, transaction_id):
        items = OrderItem.objects.filter(order=order)
        for item in items:
            product = item.cart_item.product
            product.quantity = product.quantity - item.cart_item.quantity
            product.save()
            wallet = WalletController().get(product.created_by)
            FundController().create((product.price * item.cart_item.quantity), 'EUR', order.user, payment, wallet, transaction_id, product)
            email_data = {
                'email_body': str(item.cart_item.quantity) + ' of your  product ' + product.name + ' have been ordered',
                'to_email': product.created_by.email,
                'email_subject': 'Product ordered'
                }
            send_email(email_data)

    def sendOrderConfirmation(self, user):
        email_data = {'email_body': 'Your order has been confirmed.', 'to_email': user.email, 'email_subject': 'Order confirmed'}
        send_email(email_data)
