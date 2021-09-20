from django.urls import path

from . import views

urlpatterns = [
    path('payments/stripe', views.InitiateStripePayement.as_view()),
    path('payments/stripe/<payment_intent_id>', views.ConfirmStripePayment.as_view()),
    path('payments/braintree', views.BraintreeAPIView.as_view()),
]