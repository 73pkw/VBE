from braintree.error_result import ErrorResult
from braintree.successful_result import SuccessfulResult
from .backends import BraintreeAPI, PaymentBackend
from .models import PaymentModel
from django.core.exceptions import ObjectDoesNotExist
from stripe.api_resources import line_item
from orders.models import Order, OrderItem
# from orders.serializers import OrderDetailsSerializer
from .serializers import BraintreeTransactionSerializer, PaymentSerializer, StripePaymentIntentConfirmSerializer
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
import stripe
from django.conf import settings
from cores.utils import *
from carts.models import Cart
from products.models import Product
from funds.backends import FundController
from wallets.backends import WalletController

stripe.api_key = settings.STRIPE_SECRET_KEY

class InitiateStripePayement(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        serializer = PaymentSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            customer = stripe.Customer.create(
                name=user.username,
                email=user.email
            )
            intent = stripe.PaymentIntent.create(
                payment_method_types=[payload['method']],
                amount = payload['amount'] * 100,
                currency = payload['currency'],
                customer=customer.id,
                metadata={
                    "order_number": payload['order_number']
                },
                receipt_email=user.email
            )
            serializer.save()
            response = {
                'body': {
                    'token': intent['client_secret'],
                    'public_key': settings.STRIPE_PUBLISHABLE_KEY,
                    'payment': serializer.data
                },
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_403_FORBIDDEN          
            }
        return JsonResponse(response['body'], status = response['status'], safe=False)

class ConfirmStripePayment(RetrieveUpdateAPIView):
    
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def update(self, request,payment_intent_id):
        user = request.user
        payload = json.loads(request.body)
        serializer = StripePaymentIntentConfirmSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            response = {
                'body': {
                    'error': 'Intent not valid or Order number not valid'
                },
                'status': status.HTTP_400_BAD_REQUEST            
            }

            if intent['status'] == 'succeeded' and intent['metadata']['order_number'] == payload['order_number']:
                try:
                    paymentBackend = PaymentBackend()
                    order = Order.objects.get(number=payload['order_number'], user=user)
                    payment = PaymentModel.objects.get(order_number=payload['order_number'])
                    order.status = Order.CONFIRMED
                    order.save()
                    payment.status = PaymentModel.DONE
                    payment.save()
                    paymentBackend.sendOrderConfirmation(order=order, user=user)
                    paymentBackend.updateProductsQuantity(cart=order.cart, payment=payment, payment_intent_id=payment_intent_id)
                    paymentBackend.updateOrderItemStatus(order=order, status=Order.CONFIRMED, payment_intent_id=payment_intent_id)
                    response['body'] = 'OrderDetailsSerializer(order).data'
                    response['status'] = status.HTTP_200_OK
                except ObjectDoesNotExist:
                    response['body']['error']= 'Order or payment not founded'
                    response['status'] = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_403_FORBIDDEN            
            }
        return JsonResponse(response['body'], status = response['status'], safe=False)


class BraintreeAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            braintreeApi = BraintreeAPI()
            response = {
                'body': {
                    'client_token': braintreeApi.get_client_token()
                },
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR            
            }
        return JsonResponse(response['body'], status = response['status'], safe=False)

    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        serializer = BraintreeTransactionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        paymentSerializer = PaymentSerializer(data=serializer.data['payment'])
        paymentSerializer.is_valid(raise_exception=True)

        try:
           braintreeApi = BraintreeAPI()
           apiResponse = braintreeApi.transaction_sale(payload)
           if isinstance(apiResponse, ErrorResult):
               response = {
                   'body': {
                        'error': apiResponse.message
                    },
                    'status': status.HTTP_400_BAD_REQUEST
                }
           elif isinstance(apiResponse, SuccessfulResult):
               paymentBackend = PaymentBackend()
               transaction = braintreeApi.getTransactionObject(apiResponse.transaction)
               data = paymentSerializer.data
               data['method'] = 'braintree_paypal'
               data['status'] = PaymentModel.DONE
               payment = paymentBackend.create(data=data)
               order = Order.objects.get(number=data['order_number'], user=user)
               paymentBackend.sendOrderConfirmation(order=order, user=user)
               paymentBackend.updateProductsQuantity(cart=order.cart, payment=payment, payment_intent_id=transaction['id'])
               paymentBackend.updateOrderItemStatus(order=order, status=Order.CONFIRMED, payment_intent_id=transaction['id'])
               response = {
                    'body': {
                        'data': transaction
                    },
                    'status': status.HTTP_201_CREATED
                }
        except Exception as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR          
            }
        return JsonResponse(response['body'], status = response['status'], safe=False)
