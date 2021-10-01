from orders.models import Order, OrderItem
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
import traceback
from shippings.backends import ShippoRatesAPI
from carts.serializers import CartItemSerializer
from .serializers import OrderItemSerializer

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
            ratesAPI = ShippoRatesAPI()
            ratesApiResponse = ratesAPI.get_rates(id=apiResponse['rate'])
            order_item.number = apiResponse['tracking_number']
            if(ratesApiResponse.status_code == 200):
                order_item.shipping_tax = ratesApiResponse.json()['amount']
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
            traceback.print_exc()
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class OrderItemCartItemRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request, order_id, order_item_id, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)

        try:
            serializer = CartItemSerializer(data=payload)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            order = Order.objects.get(id=order_id, user=user)
            order_item = OrderItem.objects.get(id=order_item_id, order=order)
            cart_item = order_item.cart_item
            cart_item.quantity = data['quantity']
            cart_item.save()
            order_item.total_prices = cart_item.quantity * cart_item.product.price
            order_item.save()
            response = {
                'body': OrderItemSerializer(order_item).data,
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

