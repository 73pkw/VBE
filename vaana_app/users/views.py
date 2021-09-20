from decimal import Context
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from django.template.context import RequestContext
from rest_framework import pagination
from stores.models import Store
from stores.serializers import StoreSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json
 
from .models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from cores.utils import send_email
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
 
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, ResetPasswordEmailRequestSerializer, SellerRegistrationSerializer, SetNewPasswordSerializer, UserSerializer, EmailVerificationSerializer
)
 
 
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponsePermanentRedirect
import os
from rest_framework.settings import api_settings
from addresses.serializers import AddressSerializer
from addresses.models import Address
from rest_framework import filters
from django.template.loader import get_template, render_to_string
from django.shortcuts import render
 
class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    
    def get(self, request):
        user = request.user
        if user.is_superuser == True :
            try:
                users = User.objects.all()
                serializer = UserSerializer(users, many=True)
                return JsonResponse({'users': serializer.data}, safe=False, status=status.HTTP_200_OK)
            except ObjectDoesNotExist as e:
                return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({'error':'You are not a superuser !'}, status=status.HTTP_403_FORBIDDEN)
 
class SingleUserAPIView(APIView):
    renderer_classes = (UserJSONRenderer,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get(self, request, user_id):
        owner = request.user.id
        user = User.objects.filter(id=user_id)
        if owner == user_id:
            serializer = UserSerializer(user, many=True)
            return JsonResponse({'user': serializer.data}, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error':'Forbidden !'}, status=status.HTTP_403_FORBIDDEN)
 
class CustomRedirect(HttpResponsePermanentRedirect):
 
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']
 
class SellerRegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SellerRegistrationSerializer
 
    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=RegistrationSerializer,
        security=[],
        tags=['Users'],
    )
    def post(self, request):
        user = request.data
 
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(username=user['username'], email=user['email'], password=user['password'], account_type="Seller")
       
        token = RefreshToken.for_user(user).access_token
        email = user.email
        absurl = settings.FRONT_URL + '/email/verify/'+"?token="+str(token)+ "&email="+email        
 
        context = {
            "username": user.username, 
            "email": email,
            "absurl": absurl
            }
        html_template = get_template( "email_verify.html").render(context)
 
        email_body = html_template 
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}
 
        send_email(data)
 
        return Response(RegistrationSerializer(user).data, status=status.HTTP_201_CREATED)
 
class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer
    addressSerializer = AddressSerializer
 
    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=RegistrationSerializer,
        security=[],
        tags=['Users'],
    )
    def post(self, request):
        user = request.data
 
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        address_data = user['address']
        address = Address.objects.create(country=address_data['country'], state=address_data['state'], street=address_data['street'], zipcode=address_data['zipcode'])
        user = User.objects.create_user(username=user['username'], email=user['email'], password=user['password'], account_type=user['account_type'], gender=user['gender'], address=address)
        """ addressSerializer = self.addressSerializer(data=address)
        addressSerializer.is_valid(raise_exception=True)
        serializer.data.address = addressSerializer.data
        serializer.save()
 
        user_data = serializer.data
        user = User.objects.get(email=user_data['email']) """
        token = RefreshToken.for_user(user).access_token
        email = user.email
        absurl = settings.FRONT_URL + '/email/verify/'+"?token="+str(token)+ "&email="+email        
 
        context = {
            "username": user.username, 
            "email": email,
            "absurl": absurl
            }
        html_template = get_template( "email_verify.html").render(context)
 
        # current_site = get_current_site(request).domain
        # relativeLink = reverse('email-verify')
        #absurl = 'http://'+current_site+relativeLink+"?token="+str(token)+ "&email="+ email
        email_body = html_template #+'Hi '+user.username +' \nUse the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}
 
        send_email(data)
 
        return Response(RegistrationSerializer(user).data, status=status.HTTP_201_CREATED)
 
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
            absurl = settings.FRONT_URL + '/email/verify/'+"?token="+str(token)+ "&email="+email
            email_body = 'Hi '+user.username +' \nUse the link below to verify your email \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}
            send_email(data)
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
 
 
class BecomeSeller(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    
    def update(self, request, *args, **kwargs):
        user_data = json.loads(request.body)
 
        serializer_data = {
            'account_type': user_data.get('account_type', request.user.account_type),
        }
 
        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
 
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
        # addressDict = Address.objects.get(id=user_data['address'])
        id = request.user.address
        print(id)
        # address = Address.objects.get(id=id)
        # serializer = AddressSerializer(address)

        # .update(
        #     country= user_data.get('country', dict()).get('country'),
        #     # state =user_data['state'],
        #     # street = user_data['street'],
        #     # zipcode = user_data['zipcode']
        # )
        # print(serializer.data)
        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'email': user_data.get('email', request.user.email),
            'account_type': user_data.get('account_type', request.user.account_type),
            'gender': user_data.get('gender', request.user.gender),
            # 'address' : user_data.get('address', request.user.address)
        }
        # address.country = user_data.get('country', dict()).get('country')
        # address.save()
        # request.user.address['country'] = user_data.get('country')

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
            absurl = settings.FRONT_URL + relativeLink + "?redirect_url="+redirect_url
            context = {
                "username": user.username, 
                "email": email,
                "absurl": absurl,
                "redirect_url": redirect_url
            }
            html_template = get_template( "reset_password.html").render(context)
            email_body = html_template
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            send_email(data)
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
