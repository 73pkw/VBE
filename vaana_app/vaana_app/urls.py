"""vaana_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api/', include('djoser.urls')),
    path('api/', include('users.urls'), name='users'),
    
    path('swagger-ui', schema_view.with_ui('swagger', cache_timeout=0)),

    path('api/', include('categories.urls'), name='categories'),

    path('api/', include('products.urls'), name='products'),

    path('api/', include('stores.urls'), name='stores'),
    
    path('api/', include('carts.urls'), name='carts'),

    path('api/', include('countries.urls'), name='countries'),

    path('api/', include('orders.urls'), name='orders'),

    path('api/', include('payments.urls'), name='payments'),

    path('api/', include('wishlist.urls'), name='wishlist'),

    path('api/', include('files.urls'), name='files'),

    path('api/', include('wallets.urls'), name='wallets'),
    
    # path('api/', include('chatbot.urls'), name='chatbot'),

    path('api/', include('shippings.urls'), name='shippings'),

    path('api/', include('social_auth.urls'), name='social_auth'),

    path('api/', include('newsletter.urls'), name='newsletter'),


]
