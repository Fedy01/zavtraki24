# quickresto_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.TestAPIView.as_view(), name='test_api'),
    path('customers/search/', views.SearchCustomersView.as_view(), name='search_customers'),
    path('customers/<str:customer_guid>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('businesses/', views.BusinessListView.as_view(), name='business_list'),
    path('measure-units/', views.MeasureUnitListView.as_view(), name='measure_units'),
]