
from addresses.models import Address
import json
from users.models import User
from django.contrib.auth import authenticate
import os
import random
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:

            registered_user = authenticate(
                email=email, password=settings.SOCIAL_SECRET)

            return {
                'id': registered_user.id,
                'username': registered_user.username,
                'email': registered_user.email,
                'token': registered_user.token,
                'gender': registered_user.gender,
                'account_type': registered_user.account_type,
                'address': registered_user.address.id,
            }

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        adresse = {
            "country": "to be change",
            "state": "to be change",
            "street": "to be change",
            "zipcode": "to be change"
        }
        address = Address.objects.create(**adresse)

        user = {
            'username': generate_username(name), 
            'email': email,
            'password': settings.SOCIAL_SECRET,
            'address' : address
        }
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.save()

        new_user = authenticate(
            email=email, password=settings.SOCIAL_SECRET)
        return {
            'id': new_user.id,
            'email': new_user.email,
            'username': new_user.username,
            'token': new_user.token,
            'gender': new_user.gender,
            'account_type': new_user.account_type,
            'address': new_user.address.id,
        }
