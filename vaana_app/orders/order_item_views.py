from orders.models import OrderItem
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from .backends import OrderItemBackend
from shippings.models import Shipment

class OrderItemShipmentAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, order_item_id, *args, **kwargs):
        user = request.user
        try:
            order_item = OrderItem.objects.get(id=order_item_id)
            backend = OrderItemBackend()
            apiResponse = backend.createShipment(orderItem=order_item)
            order_item.shipment = Shipment.objects.get(id=apiResponse['id'])
            order_item.save()
            response = {
                'body': apiResponse,
                'status': status.HTTP_201_CREATED
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Order item not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class OrderItemTransactionAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, order_item_id, *args, **kwargs):
        user = request.user
        try:
            order_item = OrderItem.objects.get(id=order_item_id, seller=user)
            backend = OrderItemBackend()
            apiResponse = backend.createTransaction(orderItem=order_item)
            order_item.number = apiResponse['tracking_number']
            order_item.shipping_tax = apiResponse['rate']['amount']
            order_item.save()
            response = {
                'body': apiResponse,
                'status': status.HTTP_201_CREATED
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Order item not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)
