import requests
from addresses.models import Address
from addresses.serializers import AddressSerializer
from rest_framework.decorators import permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .serializers import StoreResponseSerializer, StoreReviewResultSerializer, StoreReviewSerializer, StoreSerializer
from .models import Store, StoreReview
from rest_framework import serializers, status

import json
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.filters import SearchFilter
from cores.utils import CustomPagination
from users.models import User

class StoreSearchAPIView(ListAPIView):
    serializer_class = StoreSerializer
    queryset  = Store.objects.all()
    filter_backends =  [SearchFilter,]
    search_fields = ['name']

class LatestStoreAPIView(APIView):
    def get(self, request):
        stores = Store.objects.filter(is_active=True)[0:2]
        paginator = PageNumberPagination()

        page_size = 20
        paginator.page_size = page_size        
        page = paginator.paginate_queryset(stores, request)

        serializer = StoreSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class StoreAPIView(APIView):
    def get(self, request):
        stores = Store.objects.filter(is_active=True)
        paginator = PageNumberPagination()

        page_size = 20
        paginator.page_size = page_size        
        page = paginator.paginate_queryset(stores, request)

        serializer = StoreResponseSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @permission_classes([IsAuthenticated])
    def post(self, request):
        payload = json.loads(request.body)
        user = request.user
        serializer = StoreSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        
        response = {
            'body': {
                'error':'Unauthorized action'
            },
            'status': status.HTTP_403_FORBIDDEN
        }
        if user.account_type == User.SELLER:
            try:
                address_data = payload['address']
                address = Address.objects.create(
                    country=address_data['country'], 
                    state=address_data['state'], 
                    street=address_data['street'], 
                    zipcode=address_data['zipcode']
                )
       
                store = Store.objects.create(
                    name=payload["name"],
                    created_by=user,
                    is_active= payload["is_active"],
                    image= payload['image'],
                    address=address
                )
                serializer = StoreResponseSerializer(store)
                response['body'] = serializer.data
                response['status'] = status.HTTP_201_CREATED
            except Exception as e:
                response['body'] = {'error': str(e)}
                response['status'] = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return JsonResponse(response['body'], status=response['status'], safe=False)

class StoreProductsAPIView(APIView):
    serializer_class = ProductSerializer
    
    def get(self, request, store_id):
        try:
            store = Store.objects.get(id=store_id, is_active=True)
            products = Product.objects.filter(store=store)
            paginator = CustomPagination()

            paginator.page_size = 20        
            page = paginator.paginate_queryset(products, request)

            serializer = ProductSerializer(page, many=True)
            response = {
                'body': paginator.get_paginated_response(serializer.data),
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

class StoreUpdateDeleteAPIView(RetrieveUpdateAPIView):
    def get(self, request, store_id):
        try:
            store = Store.objects.get(id=store_id)
            serializer = StoreResponseSerializer(store)
            response = {
                'body': serializer.data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)
        
    @permission_classes([IsAuthenticated])
    def put(self, request, store_id):
        user = request.user
        payload = json.loads(request.body)
        try:
            store = Store.objects.get(id=store_id)
            store_item = Store.objects.filter(created_by=user, id=store_id)
            address_id = store.address.id
            address = Address.objects.select_related().filter(id=address_id).update(
                country=payload.get('address', dict()).get('country'),
                state=payload.get('address', dict()).get('state'),
                zipcode=payload.get('address', dict()).get('zipcode'),
                street=payload.get('address', dict()).get('street'),
                updated_at=now()
            )
            # store_item.update(
            #     name=payload['name'],
            #     is_active=payload['is_active'],
            #     updated_at=now()
            # )
            store.name = payload['name']
            store.is_active = payload['is_active']
            store.image = payload['image']
            store.save()
            
            serializer = StoreResponseSerializer(store)
            response = {
                'body': serializer.data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        
        return JsonResponse(response['body'], status=response['status'], safe=False)

    @permission_classes([IsAuthenticated])
    def delete(self, request, store_id):
        user = request.user.id
        try:
            store = Store.objects.get(created_by=user, id=store_id)
            store.delete()
            response = {
                'body': 'Success',
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

class SellerStoreAPIView(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request):
        user = request.user
        stores = Store.objects.filter(created_by=user)
        paginator = PageNumberPagination()
        paginator.page_size = 20        
        page = paginator.paginate_queryset(stores, request)
        serializer = StoreResponseSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

class RegionStoreAPIView(APIView):
    @csrf_exempt
    def get(self, request, country):
        countries = requests.get('https://restcountries.com/v3/all')
        response = {
            'body': {
                'error': 'bad response from api'
            },
            'status': status.HTTP_502_BAD_GATEWAY
        }

        if countries.status_code == 200:
            for country in countries:
                if country.name == country:
                    region = country.region
            print(region)
            response['body'] = countries.json()
            response['status'] = status.HTTP_200_OK
            
        return JsonResponse(response['body'], safe=False, status=response['status'])

class StoreReviewsAPIView(APIView):
    serializer_class = StoreReviewSerializer

    def get(self, request, store_id):
        try:
            store = Store.objects.get(id=store_id, is_active=True)
            reviews = StoreReview.objects.filter(store=store)
            paginator = CustomPagination()
            paginator.page_size = 20        
            page = paginator.paginate_queryset(reviews, request)

            serializer = StoreReviewResultSerializer(page, many=True)
            response = {
                'body': paginator.get_paginated_response(serializer.data),
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request):
        payload = json.loads(request.body)
        user = request.user
        serializer = StoreReviewSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            store = Store.objects.get(id=payload['store'])
            review = StoreReview.objects.create(
                title=payload["title"],
                comment=payload["comment"],
                rating=payload["rating"],
                store=store,
                user=user
            )
            response = {
                'body': StoreReviewResultSerializer(review).data,
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

class StoreReviewUpdateDeleteAPIView(RetrieveUpdateAPIView):
    def get(self, request, review_id):
        try:
            review = StoreReview.objects.get(id=review_id)
            serializer = StoreReviewResultSerializer(review)
            response = {
                    'body': serializer.data,
                    'status': status.HTTP_200_OK
                }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)
    
    @permission_classes([IsAuthenticated])
    def put(self, request, review_id):
        user = request.user
        payload = json.loads(request.body)
        try:
            review_item = StoreReview.objects.filter(user=user, id=review_id)
            review_item.update(
                **payload,
                updated_at=now()
                )
            review = StoreReview.objects.get(id=review_id)
            serializer = StoreReviewResultSerializer(review)
            response = {
                    'body': serializer.data,
                    'status': status.HTTP_200_OK
                }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

    @permission_classes([IsAuthenticated])
    def delete(self, request, review_id):
        user = request.user
        try:
            review = StoreReview.objects.get(user=user, id=review_id)
            review.delete()
            response = {
                'body': 'Success',
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist as e:
            response = {
                'body': {
                    'error': str(e)
                },
                'status': status.HTTP_404_NOT_FOUND
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

