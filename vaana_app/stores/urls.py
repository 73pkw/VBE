from django.urls import path
from . import views

urlpatterns = [
  path('stores', views.StoreAPIView.as_view()),
  path('stores/', views.StoreSearchAPIView.as_view()),
  path('stores/<uuid:store_id>', views.StoreUpdateDeleteAPIView.as_view()),
  path('stores/<uuid:store_id>/products', views.StoreProductsAPIView.as_view()),
  path('stores/latest', views.LatestStoreAPIView.as_view()),
  path('stores/sellers', views.SellerStoreAPIView.as_view()),
  path('stores/region', views.RegionStoreAPIView.as_view()),

  path('stores/reviews', views.StoreReviewsAPIView.as_view()),
  path('stores/reviews/<uuid:review_id>', views.StoreReviewUpdateDeleteAPIView.as_view()),
]
