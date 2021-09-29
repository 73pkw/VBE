from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import CreditCardSerializer, BankAccountSerializer, PaymentMethodSerializer
from .models import CreditCard, BankAccount, PaymentMethod

class CreditCardAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = CreditCardSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
            response = {
                'body': serializer.data,
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            cards = CreditCard.objects.filter(user=user)
            response = {
                'body': CreditCardSerializer(cards, many=True).data,
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class CreditCardRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, card_id):
        user = request.user

        try:
            card = CreditCard.objects.get(id=card_id, user=user)
            response = {
                'body': CreditCardSerializer(card).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Card not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request, card_id):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = CreditCardSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            card = CreditCard.objects.get(id=card_id, user=user)
            card.update(payload)
            response = {
                'body': CreditCardSerializer(card).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Card not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def delete(self, request, card_id):
        user = request.user

        try:
            card = CreditCard.objects.get(id=card_id, user=user)
            card.delete()
            response = {
                'body': 'Card removed succefully',
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Card not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class BankAccountAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = BankAccountSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            response = {
                'body': serializer.data,
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)


    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            accounts = BankAccount.objects.filter(user=user)
            response = {
                'body': BankAccountSerializer(accounts, many=True).data,
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class BankAccountRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, account_id):
        user = request.user

        try:
            account = BankAccount.objects.get(id=account_id, user=user)
            response = {
                'body': BankAccountSerializer(account).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Account not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request, account_id):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = BankAccountSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            account = BankAccount.objects.get(id=account_id, user=user)
            account.update(payload)
            response = {
                'body': BankAccountSerializer(account).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Account not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def delete(self, request, account_id):
        user = request.user

        try:
            account = BankAccount.objects.get(id=account_id, user=user)
            account.delete()
            response = {
                'body': 'Account delete succefully',
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Account not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class PaymentMethodAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = PaymentMethodSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
            response = {
                'body': serializer.data,
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class PaymentMethodRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request, payment_method_id):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = PaymentMethodSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        
        try:
            paymentMethod = PaymentMethod.objects.get(id=payment_method_id, user=user)
            paymentMethod.update(payload)
            response = {
                'body': PaymentMethodSerializer(paymentMethod).data,
                'status': status.HTTP_201_CREATED
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Payment method not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

