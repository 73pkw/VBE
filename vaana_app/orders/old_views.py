# from rest_framework.generics import RetrieveAPIView
# from shippings.models import ShippingMethod
# from addresses.models import Address
# from carts.models import Cart
# from .models import Order, ShippingAddress
# from .serializers import OrderDetailsSerializer, OrderItemDetailsSerializer, OrderSerializer, ShippingAddressSerializer, OrderItemSerializer
# from shippings.serializers import ShippingMethodSerializer
# from products.serializers import ProductResponseSerializer
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework import serializers, status
# import json
# from django.core.exceptions import ObjectDoesNotExist
# from .utils import Util
# from rest_framework.decorators import permission_classes
# from cores.utils import *
# from .services import *
# from django.utils.timezone import now
# from funds.backends import *


# class InitiateOrderApiView(APIView):
#     @csrf_exempt
#     @permission_classes([IsAuthenticated])
#     def post(self, request, *args, **kwargs):
#         user = request.user
#         payload = json.loads(request.body)
#         serializer = OrderSerializer(data=payload)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.data
#         number = Util.getOrderNumber()
#         shipping_address_data = data['shipping_address']
#         address_data = shipping_address_data['address']
#         shipping_method_data = data['shipping_method']

#         try:
#             cart = Cart.objects.get(id=data['cart'], status=Cart.OPEN)
#             address = Address.objects.create(country=address_data["country"], state=address_data['state'], street=address_data['street'], zipcode=address_data['zipcode'])
#             shipping_address = ShippingAddress.objects.create(address=address, phone_number=shipping_address_data['phone_number'], notes=shipping_address_data['notes'])
#             shipping_method = ShippingMethod.objects.create(name=shipping_method_data['name'], price=shipping_method_data['price'], currency=shipping_method_data['currency'])
#             order = Order.objects.create(
#                 number=number, 
#                 user=user, 
#                 cart=cart, 
#                 currency=data['currency'], 
#                 shipping_address=shipping_address,
#                 total_tax=data['total_tax'],
#                 shipping_tax=data['shipping_tax'],
#                 total_prices=data['total_prices'],
#                 shipping_method=shipping_method
#                 )
#             OrderService().create_order_items(order)
#             cart.status = Cart.SUBMITTED
#             cart.save()
#             response = {
#                 'body': OrderDetailsSerializer(order).data,
#                 'status': status.HTTP_201_CREATED
#             }
#         except Exception as e:
#             response = {
#                 'body': {
#                     'error': str(e)
#                 },
#                 'status': status.HTTP_500_INTERNAL_SERVER_ERROR
#             }
#         return JsonResponse(response['body'], status=response['status'], safe=False)

# class GetCustomerOrderAPIView(APIView):
#     @csrf_exempt
#     @permission_classes([IsAuthenticated])
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         orders = Order.objects.filter(user=user)
#         serializer = OrderDetailsSerializer(orders, many=True)

#         return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

# class GetSellerOrderAPIView(APIView):
#     @csrf_exempt
#     @permission_classes([IsAuthenticated])
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         orders = OrderItem.objects.filter(seller=user)
#         serializer = OrderItemDetailsSerializer(orders, many=True)

#         return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

# class OrderDetailsAPIView(APIView):
#     @csrf_exempt
#     @permission_classes([IsAuthenticated])
#     def get(self, request, id):
#         user = request.user

#         try:
#             order = Order.objects.get(id=id, user=user)
#             response = {
#                 'body': OrderDetailsSerializer(order).data,
#                 'status': status.HTTP_200_OK
#             }
#         except ObjectDoesNotExist as e:
#             response = {
#                 'body': {
#                     'error': str(e)
#                 },
#                 'status': status.HTTP_404_NOT_FOUND
#             }

#         return JsonResponse(response['body'], status = response['status'], safe=False)
    
#     @csrf_exempt
#     @permission_classes([IsAuthenticated])
#     def delete(self, request, id):
#         user = request.user
#         fund = FundController()

#         try:
#             order_item = OrderItem.objects.get(id=id)
#             response = {
#                 'body': {
#                     'error': 'Unauthorized action'
#                 },
#                 'status': status.HTTP_403_FORBIDDEN
#             }
#             if order_item.order.user == user and order_item.status in (OrderItem.INITIATED, OrderItem.CONFIRMED):
#                 order_item.status = OrderItem.CANCELED
#                 order_item.updated_at = now()
#                 order_item.save()
#                 fund.cancel(order_item.payment_intent_id)
#                 response['body'] = OrderItemSerializer(order_item).data
#                 response['status'] = status.HTTP_200_OK
#         except ObjectDoesNotExist as e:
#             response = {
#                 'body': {
#                     'error': str(e)
#                 },
#                 'status': status.HTTP_404_NOT_FOUND
#             }

#         return JsonResponse(response['body'], status = response['status'], safe=False)


