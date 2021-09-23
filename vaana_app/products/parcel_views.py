from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from .models import Parcel, Product
from .serializers import ParcelSerializer

class ParcelAPIVIew(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, product_id, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['created_by'] = user.id
        serializer = ParcelSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            product = Product.objects.get(id=product_id, created_by=user)
            serializer.save()
            product.parcel = serializer.data['id']
            product.save()
            response = {
                'body': serializer.data,
                'status': status.HTTP_201_CREATED
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Product not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class ParcelRetrieveUpdataAPIView(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, parcel_id):
        user = request.user

        try:
            parcel = Parcel.objects.get(id=parcel_id, created_by=user)
            response = {
                'body': ParcelSerializer(parcel).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Parcel not found',
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
    def put(self, request, parcel_id):
        user = request.user
        payload = json.loads(request.body)
        serializer = ParcelSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            parcel = Parcel.objects.get(id=parcel_id, created_by=user)
            parcel.update(payload)
            response = {
                'body': ParcelSerializer(parcel).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Parcel not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)
