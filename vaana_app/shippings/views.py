from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Shipment, Transaction, Address
import json
from rest_framework import serializers, status


from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .backends import ShippoCarrierAPI, ShippoRatesAPI, ShippoShipmentAPI, ShippoTransactionAPI, ShippoTrackingAPI
from .serializers import ShippoAddressSerializer, ShippoShipmentSerializer, ShippoTransactionSerializer
from rest_framework.generics import  RetrieveUpdateAPIView

class ShippoCarrierAPIVIew(APIView):
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        carrierApi = ShippoCarrierAPI()
        page = request.query_params.get('page')

        try:
            apiResponse = carrierApi.all(page)
            response = {
                'body': apiResponse.json(),
                'status': apiResponse.status_code
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class ShippoShipmentAPIView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        playload = json.loads(request.body)
        shipmentSerializer = ShippoShipmentSerializer(data=playload)
        shipmentSerializer.is_valid(raise_exception=True)
        shipmentApi = ShippoShipmentAPI()

        try:
            shipmentSerializer.save()
            data = shipmentSerializer.data
            apiResponse = shipmentApi.create(data)
            shipment = Shipment.objects.get(id=data['id'])
            shipment.object_id = apiResponse['object_id']
            shipment.save()
            response = {
                'body': {
                    'api_response': apiResponse,
                    'data': ShippoShipmentSerializer(shipment).data
                },
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }        
        
        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        shipmentApi = ShippoShipmentAPI()
        page = request.query_params.get('page')
        objects_id = request.query_params.get('objects_id')

        try:
            apiResponse = shipmentApi.retrieve(objects_id) if objects_id is not None else shipmentApi.all(page)
            response = {
                'body': apiResponse.json(),
                'status': apiResponse.status_code
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class ShippoTransactionAPIView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        playload = json.loads(request.body)
        serializer = ShippoTransactionSerializer(data=playload)
        serializer.is_valid(raise_exception=True)
        transactionApi = ShippoTransactionAPI()

        try:
            shipment = Shipment.objects.get(id=playload['shipment'])
            data = {
                'shipment': ShippoShipmentSerializer(shipment).data,
                'servicelevel_token': playload['servicelevel_token'],
                'carrier_account': playload['carrier_account']
            }
            serializer.save()
            apiResponse = transactionApi.create(data)
            transaction = Transaction.objects.get(id=serializer.data['id'])
            transaction.object_id = apiResponse['object_id']
            transaction.save()
            response = {
                'body': apiResponse,
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        transactionApi = ShippoTransactionAPI()
        page = request.query_params.get('page')
        objects_id = request.query_params.get('objects_id')

        try:
            apiResponse = transactionApi.retrieve(objects_id) if objects_id is not None else transactionApi.all(page)
            response = {
                'body': apiResponse.json(),
                'status': apiResponse.status_code
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class ShippoRatesAPIView(APIView):
    @csrf_exempt
    def get(self, request, shipment_object_id, *args, **kwargs):
        page = request.query_params.get('page')
        currency = request.query_params.get('currency')
        ratesApi = ShippoRatesAPI()

        try:
            apiResponse = ratesApi.get_rates_for_shipment(shipment_object_id=shipment_object_id, page=page, currency=currency)
            response = {
                'body': apiResponse.json(),
                'status': apiResponse.status_code
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        return JsonResponse(response['body'], status=response['status'], safe=False)

class ShippoTrackingAPIView(APIView):
    def get(self, request, carrier, tracking_number):
        trackingApi = ShippoTrackingAPI()
        try:
            apiResponse = trackingApi.get(carrier=carrier, tracking_number=tracking_number)
            response = {
                'body': apiResponse.json(),
                'status': apiResponse.status_code
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)

class ShippoAddressAPIView(APIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = ShippoAddressSerializer(data=payload)
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
            addresses = Address.objects.filter(user=user)
            response = {
                'body': ShippoAddressSerializer(addresses, many=True).data,
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)


class ShippoAddressRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def get(self, request, address_id):
        user = request.user
        try:
            address = Address.objects.get(id=address_id, user=user)
            response = {
                'body': ShippoAddressSerializer(address).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Address not found',
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
    def put(self, request, address_id):
        user = request.user
        payload = json.loads(request.body)
        payload['user'] = user.id
        serializer = ShippoAddressSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        try:
            address = Address.objects.get(id=address_id, user=user)
            address.update(payload)
            response = {
                'body': ShippoAddressSerializer(address).data,
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Address not found',
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
    def delete(self, request, address_id):
        user = request.user
        try:
            address = Address.objects.get(id=address_id, user=user)
            address.delete()
            response = {
                'body': 'Address removed succefully',
                'status': status.HTTP_200_OK
            }
        except ObjectDoesNotExist:
            response = {
                'body': 'Address not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            response = {
                'body': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

        return JsonResponse(response['body'], status=response['status'], safe=False)
