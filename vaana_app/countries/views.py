from django.shortcuts import render
from requests import api

from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from django.core.exceptions import ObjectDoesNotExist
import requests
from .models import *
from .serializers import *


class CountryView(APIView):

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        api_response = requests.get('https://restcountries.com/v3/all')
        #countries = Country.objects.all()
        # TODO: stock response in database 

        response = {
            'body': {
                'error': 'bad response from api'
            },
            'status': status.HTTP_502_BAD_GATEWAY
        }
        
        if api_response.status_code == 200:
            response['body'] = api_response.json()
            response['status'] = status.HTTP_200_OK
            
        return JsonResponse(response['body'], safe=False, status=response['status'])
