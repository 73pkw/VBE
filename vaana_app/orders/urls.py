from django.urls import path

from . import views, order_item_views

urlpatterns = [
    path('orders/initiate', views.OrderInitiateAPIView.as_view()),
    # path('orders/customers', views.GetCustomerOrderAPIView.as_view()),
    # path('orders/sellers', views.GetSellerOrderAPIView.as_view()),
    path('orders/items/<order_item_id>', views.OrderItemRetrieveUpdateAPIVIew.as_view()),
    path('orders/items/<order_item_id>/shipments', order_item_views.OrderItemShipmentAPIView.as_view()),
    path('orders/items/<order_item_id>/transactions', order_item_views.OrderItemTransactionAPIView.as_view()),
]
