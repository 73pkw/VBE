from braintree.error_result import ErrorResult
from braintree.successful_result import SuccessfulResult
from .backends import BraintreeAPI, PaymentBackend
from .models import Payment
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from django.conf import settings
from .serializers import BraintreeTransactionSerializer, PaymentSerializer, StripePaymentIntentConfirmSerializer
from .backends import StripeAPI, BraintreeAPI
from orders.models import Order, OrderItem
from orders.serializers import OrderDetailsSerializer
from carts.models import Cart

class InitiateStripePayement(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = PaymentSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(id=payload['order'], user=user)
            stripeApi = StripeAPI()
            intent = stripeApi.getPaymentIntent(user=user, data=payload, order=order)
            serializer.save()
            response = {
                'body': {
                    'token': intent['client_secret'],
                    'public_key': settings.STRIPE_PUBLISHABLE_KEY,
                    'payment': serializer.data
                },
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': str(e),
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class ConfirmStripePayment(RetrieveUpdateAPIView):
    
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request,payment_intent_id):
        user = request.user
        payload = json.loads(request.body)
        serializer = StripePaymentIntentConfirmSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(id=payload['order'], user=user)
            stripeApi = StripeAPI()
            intent = stripeApi.retrievePaymentIntent(payment_intent_id=payment_intent_id)
            response = {
                'body': {
                    'error': 'Intent not valid or Order number not valid'
                },
                'status': status.HTTP_400_BAD_REQUEST            
            }
            if intent['status'] == 'succeeded' and intent['metadata']['order'] == payload['order']:
                cart = order.cart
                cart.status = Cart.SUBMITTED
                cart.save()
                payment = Payment.objects.get(order=order.id)
                payment.status = Payment.DONE
                payment.save()
                paymentBackend = PaymentBackend()
                paymentBackend.sendOrderConfirmation(user=user)
                paymentBackend.updateOrderItemStatus(order=order, status=OrderItem.CONFIRMED, payment_intent_id=payment_intent_id)
                paymentBackend.updateProductsQuantity(order=order, payment=payment, transaction_id=payment_intent_id)
                response['body'] = OrderDetailsSerializer(order).data
                response['status'] = status.HTTP_200_OK

        except ObjectDoesNotExist as e:
            response = {
                'body': str(e),
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

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

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        serializer = BraintreeTransactionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        paymentSerializer = PaymentSerializer(data=serializer.data['payment'])
        paymentSerializer.is_valid(raise_exception=True)
        try:
           data = paymentSerializer.data
           order = Order.objects.get(number=data['order'], user=user)
           braintreeApi = BraintreeAPI()
           apiResponse = braintreeApi.transaction_sale(data=payload, user=user)
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
               cart = order.cart
               cart.status = Cart.SUBMITTED
               cart.save()
               data['method'] = 'braintree_paypal'
               data['status'] = Payment.DONE
               data['user'] = user.id
               payment = paymentBackend.create(data=data)
               paymentBackend.sendOrderConfirmation(user=user)
               paymentBackend.updateOrderItemStatus(order=order, status=Order.CONFIRMED, payment_intent_id=transaction['id'])
               paymentBackend.updateProductsQuantity(order=order, payment=payment, transaction_id=transaction['id'])
               response = {
                    'body': {
                        'data': transaction
                    },
                    'status': status.HTTP_201_CREATED
                }
        except ObjectDoesNotExist as e:
            response = {
                'body': str(e),
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR          
            }
        return JsonResponse(response['body'], status = response['status'], safe=False)
