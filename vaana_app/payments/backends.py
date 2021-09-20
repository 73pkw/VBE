import braintree
from django.conf import settings
from .models import PaymentModel
from cores.utils import *
from funds.backends import FundController
from wallets.backends import WalletController
from orders.models import Order, OrderItem

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY
    )
)

class BraintreeAPI(object):
    def get_client_token(self):
        return gateway.client_token.generate()

    def transaction_sale(self, data, user=None):
        return gateway.transaction.sale({
            "amount": data['amount'],
            "payment_method_nonce": data['nonce'],
            "device_data": data['device_data'] if 'device_data' in data else None,
            "customer":{
                "email": 'alioune.kanoute@terinnova.com'
                #user.email,
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

class PaymentBackend(object):
    def create(self, data):
        return PaymentModel.objects.create(
            order_number=data['order_number'],
            method=data['method'],
            amount=data['amount'],
            currency=data['currency'],
            status=data['status'] if 'status' in data else PaymentModel.OPEN
        )
    
    def updateOrderItemStatus(self, order, status, payment_intent_id):
        items = OrderItem.objects.filter(order=order)
        for item in items:
            item.payment_intent_id = payment_intent_id
            item.status = status
            item.save()

    def updateProductsQuantity(self, cart, payment, payment_intent_id):
        for item in cart.items.all():
            try:
                product = item.product
                product.quantity = product.quantity - item.quantity
                product.save()
                wallet = WalletController().get(product.created_by)
                FundController().create((product.price * item.quantity), 'EUR', cart.owner, payment, wallet, payment_intent_id, product)
                email_data = {
                    'email_body': str(item.quantity) + ' of your  product ' + product.name + ' have been ordered',
                    'to_email': product.created_by.email,
                    'email_subject': 'Product ordered'
                    }
                send_email(email_data)
            except Exception as e:
                print(str(e))
                pass

    def sendOrderConfirmation(self, order, user):
        email_data = {'email_body': 'Your order ' + order.number + ' has been confirmed.', 'to_email': user.email, 'email_subject': 'Order confirmed'}
        send_email(email_data)
