from django.urls import path

from . import views

from . import payment_method_views

urlpatterns = [
    path('payments/stripe', views.InitiateStripePayement.as_view()),
    path('payments/stripe/<payment_intent_id>', views.ConfirmStripePayment.as_view()),
    path('payments/braintree', views.BraintreeAPIView.as_view()),
    path('payments/cards', payment_method_views.CreditCardAPIView.as_view()),
    path('payments/cards/<card_id>', payment_method_views.CreditCardRetrieveUpdateAPIView.as_view()),
    path('payments/accounts', payment_method_views.BankAccountAPIView.as_view()),
    path('payments/accounts/<account_id>', payment_method_views.BankAccountRetrieveUpdateAPIView.as_view()),
    path('payments/methods', payment_method_views.PaymentMethodAPIView.as_view()),
    path('payments/methods/<payment_method_id>', payment_method_views.PaymentMethodRetrieveUpdateAPIView.as_view()),
]