from logging import exception
from rest_framework.serializers import Serializer
from .models import Cart, CartItem
from .serializers import CartDetailsSerializer, CartSerializer, CartItemSerializer
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product
from .services import *


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CartAddView(APIView):

    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=CartSerializer,
        security=[],
        tags=['Carts'],
    )
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user

        response = {
            'body': {
                'error': 'This user already have an open cart'
            },
            'status': status.HTTP_400_BAD_REQUEST
        }

        try:
            cart = Cart.objects.get(owner = user, status = Cart.OPEN)
            response ['body']['data'] = CartDetailsSerializer(cart).data
            
        except Exception:
            try:
                cart = Cart.objects.create(owner=user, status = Cart.OPEN)
                serializer = CartDetailsSerializer(cart)
                response['body'] = serializer.data
                response['status'] = status.HTTP_201_CREATED

            except Exception as exception:
                response['body']['error'] = str(exception)
                response['status'] = status.HTTP_500_INTERNAL_SERVER_ERROR  

        return JsonResponse(response['body'], status = response['status'])

    @swagger_auto_schema(
        operation_description="apiview post description override",
        security=[],
        tags=['Carts'],
    )
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            cart = Cart.objects.get(owner = user, status = Cart.OPEN)
            response = {
                'body': CartDetailsSerializer(cart).data,
                'status': status.HTTP_200_OK
            }
        except Exception:
            try:
                cart = Cart.objects.create(owner=user, status = Cart.OPEN)
                serializer = CartDetailsSerializer(cart)
                response = {
                    'body': serializer.data,
                    'status': status.HTTP_200_OK
                }
            except Exception as exception:
                response = {
                    'body': {
                        'error': str(exception)
                    },
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                }

        return JsonResponse(response['body'], status = response['status'])

class CartUpdateAPIView(RetrieveUpdateAPIView):
    @swagger_auto_schema(
        operation_description="apiview post description override",
        security=[],
        tags=['Carts'],
        request_body=CartItemSerializer
    )
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def put(self, request, id):
        user = request.user
        payload = json.loads(request.body)
        cartService = CartService()
        try:
            cart = Cart.objects.get(id=id, owner=user, status = Cart.OPEN)
        except ObjectDoesNotExist:
            cart = Cart.objects.create(owner=user, status = Cart.OPEN)

        for item in payload:
            serializer = CartItemSerializer(data=item)
            serializer.is_valid(raise_exception=True) 
            product = Product.objects.get(id=item['product'])
            if cartService.itemInCart(cart, product.id) == False and product.quantity > item['quantity']:
                item = CartItem.objects.create(product=product, quantity=item['quantity'])
                cart.items.add(item)
        serializer = CartDetailsSerializer(cart)
        response = {
            'body': serializer.data,
            'status': status.HTTP_200_OK
        }
        
        return JsonResponse(response['body'], status = response['status'])

        
class CartItemView(APIView):
    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=CartItemSerializer,
        security=[],
        tags=['Carts'],
    )
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        serializer = CartItemSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(id=payload['product'])
        response = {
            'body': {
                'error': 'quantity not allowed'
            },
            'status': status.HTTP_400_BAD_REQUEST
        }

        if product.quantity > payload['quantity']:
                
                try:
                    cart = Cart.objects.get(owner=user, status = Cart.OPEN)
                except ObjectDoesNotExist:
                    cart = Cart.objects.create(owner=user, status = Cart.OPEN)

                item = CartItem.objects.create(product=product, quantity=payload['quantity'])
                
                cart.items.add(item)
                response['body'] = CartDetailsSerializer(cart).data
                response['status'] = status.HTTP_201_CREATED
                
        return JsonResponse(response['body'], status = response['status'])


class CartItemUpdateView(RetrieveUpdateAPIView):

        @swagger_auto_schema(
            operation_description="apiview post description override",
            request_body=CartItemSerializer,
            security=[],
            tags=['Carts'],
        )
        @permission_classes([IsAuthenticated])
        def put(self, request, id):
            user = request.user
            payload = json.loads(request.body)
            serializer = CartItemSerializer(data=payload)
            serializer.is_valid(raise_exception=True)

            product = Product.objects.get(id=payload['product'])
            quantity = payload['quantity']
            response = {
                'body': {
                    'error': 'quantity not allowed'
                },
                'status': status.HTTP_400_BAD_REQUEST
            }
            if product.quantity > quantity:
                try:
                    cart = Cart.objects.get(owner=user, status = Cart.OPEN)
                    
                    try:
                        cart_item = CartItem.objects.get(id=id)
                        cart_item.quantity = quantity
                        cart_item.save()
                        response['body'] = CartDetailsSerializer(cart).data
                        response['status'] = status.HTTP_200_OK
                    except ObjectDoesNotExist as e:
                        response['body']['error'] = 'Item not founded'
                        response['status'] = status.HTTP_404_NOT_FOUND
                except ObjectDoesNotExist as e:
                    response['body']['error'] = 'Any opened cart founded'
                    response['status'] = status.HTTP_400_BAD_REQUEST

            return JsonResponse(response['body'], status = response['status'], safe=False)

        @csrf_exempt
        @permission_classes([IsAuthenticated])
        def delete(self, request, id):
            user = request.user

            try:
                
                cart = Cart.objects.get(owner=user, status = Cart.OPEN)
                try:
                    cart_item = CartItem.objects.get(id=id)
                    cart.items.remove(cart_item)
                    response = {
                        'body': CartDetailsSerializer(cart).data,
                        'status': status.HTTP_200_OK
                    }
                except ObjectDoesNotExist:
                    response = {
                        'body': {
                            'error': 'Cart item not founded'
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    }

            except ObjectDoesNotExist:
                response = {
                    'body': {
                        'error': 'Any open cart founded'
                    },
                    'status': status.HTTP_404_NOT_FOUND
                }

            return JsonResponse(response['body'], status = response['status'], safe=False)
