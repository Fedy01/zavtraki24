from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path('promotions/', views.promotions, name='promotions'),
    path("make_order/", views.make_order, name="make_order"),
]
