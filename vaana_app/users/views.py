from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from rest_framework import pagination
from stores.models import Store
from stores.serializers import StoreSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json

from .models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, UserSerializer, EmailVerificationSerializer
)


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponsePermanentRedirect
import os
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework import viewsets



class StandardResultsSetPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'current_page': int(self.request.query_params.get('page', 1)),
            'total': self.page.paginator.count,
            'per_page': self.page_size,
            'total_pages': round(self.page.paginator.count/self.page_size, 1),
            'data': data,
        })
class UserAPIView(ListAPIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    # pagination_class = LimitOffsetPagination
    
    def get(self, request):
        queryset = User.objects.all()
        paginator = StandardResultsSetPagination()

        page_size = 5
        paginator.page_size = page_size        
        page = paginator.paginate_queryset(queryset, request)

        serializer = UserSerializer(page, many=True)
        result = paginator.get_paginated_response(serializer.data)
        return paginator.get_paginated_response(serializer.data)

class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=RegistrationSerializer,
        security=[],
        tags=['Users'],
    )
    def post(self, request):
        user = json.loads(request.body)

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        email = user.email

        # token = user_data['token']
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        #absurl = 'http://'+current_site+relativeLink+"?token="+str(token)+ "&email="+ email
        absurl = 'http://localhost:4200/email/verify/'+"?token="+str(token)+ "&email="+email        
        email_body = 'Hi '+user.username +' \nUse the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)

class ResendEmailAPI(APIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post (self, request):
        user = json.loads(request.body)
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        try:
            email = serializer.data['email']
            user = User.objects.get(email=email)
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-resend')

            #absurl = 'http://'+current_site+relativeLink+"?token="+str(token)+ email
            absurl = 'http://localhost:4200/email/verify/'+"?token="+str(token)+ "&email="+email
            email_body = 'Hi '+user.username +' \nUse the link below to verify your email \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}
            Util.send_email(data)
            return Response({'code': '200'} , status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'code': '400'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return JsonResponse({'code': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class VerifyEmail(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get('token')
        #email = re
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            # print(payload['user'])

            if not user.is_verified:
                user.is_verified = True
                user.save()
            return JsonResponse({'code': '200'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return JsonResponse({'code': '400'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

          
class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=LoginSerializer,
        security=[],
        tags=['Users'],
    )
    def post(self, request):
        user = json.loads(request.body)

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="apiview post description override",
        security=[],
        tags=['Users'],
    )
    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=UserSerializer,
        security=[],
        tags=['Users'],
    )    
    def update(self, request, *args, **kwargs):
        user_data = json.loads(request.body)

        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'email': user_data.get('email', request.user.email),
            'account_type': user_data.get('account_type', request.user.account_type),
            'gender': user_data.get('gender', request.user.gender),
        }

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(APIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            #absurl = 'http://'+current_site + relativeLink
            absurl = 'http://localhost:4200' + relativeLink
            email_body = 'Hello, \nUse link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
            return Response({'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'Your are not a user please register !'}, status=status.HTTP_404_NOT_FOUND)


class PasswordTokenCheckAPI(APIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True, 'message': 'Credentials valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            #if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



class SetNewPasswordAPIView(APIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class UserStoreAPIView(APIView):
    serializer_class = StoreSerializer

    def get(self, request, user_id):
        stores = Store.objects.filter(created_by=user_id)
        serializer = StoreSerializer(stores, many=True)
        return JsonResponse({'user stores': serializer.data}, safe=False, status=status.HTTP_200_OK)
