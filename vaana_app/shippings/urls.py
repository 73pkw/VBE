from django.urls import path

from . import views

urlpatterns = [

    path('shippings/carriers', views.ShippoCarrierAPIVIew.as_view()),
    path('shippings/shipments', views.ShippoShipmentAPIView.as_view()),
    path('shippings/transactions', views.ShippoTransactionAPIView.as_view()),
    path('shippings/rates/<shipment_object_id>', views.ShippoRatesAPIView.as_view()),
    path('shippings/tracks/<carrier>/<tracking_number>', views.ShippoTrackingAPIView.as_view()),
    path('shippings/addresses', views.ShippoAddressAPIView.as_view()),
    path('shippings/addresses/<address_id>', views.ShippoAddressRetrieveUpdateAPIView.as_view()),
]
