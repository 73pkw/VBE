from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import OrderDetailsSerializer, OrderSerializer, OrderItemSerializer
from carts.models import Cart
from .models import Order, OrderItem
from .backends import OrderBackends, SellerCustomerBackend

class OrderInitiateAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = OrderSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            data = serializer.data
            cart = Cart.objects.get(id=data['cart'])
            order = Order.objects.get(id=data['id'])
            backend = OrderBackends()
            order_items = backend.createOrderItems1(order=order, cart=cart)
            response = {
                'body': OrderDetailsSerializer(order).data,
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class OrderItemRetrieveUpdateAPIVIew(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request, order_item_id):
        user = request.user
        payload = json.loads(request.body)
        
        try:
            order_item = OrderItem.objects.get(id=order_item_id)
            order_item.update(data=payload)
            response = {
                'body': OrderItemSerializer(order_item).data,
                'status': status.HTTP_200_OK
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

class GetCustomerOrderAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        orders = Order.objects.filter(user=user)
        serializer = OrderDetailsSerializer(orders, many=True)

        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

class GetSellerOrderAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        orders = OrderItem.objects.filter(seller=user)
        serializer = OrderItemSerializer(orders, many=True)

        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
        
class SellerCustomerAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        orders = OrderItem.objects.filter(seller=user)
        backend = SellerCustomerBackend()
        users = backend.getCustomers(orderItems=orders)

        return JsonResponse(users, status=status.HTTP_200_OK, safe=False)
