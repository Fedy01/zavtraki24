from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from main.api import MenuItemViewSet
from django.contrib.auth import views as auth_views
from django.contrib import admin  # ← ДОБАВЬТЕ ЭТО!
from django.urls import path, include

router = DefaultRouter()
router.register(r'menu', MenuItemViewSet, basename='menu')

urlpatterns = [

    *router.urls,
    path('admin/', admin.site.urls),
    path('webhook/quickresto/', views.quickresto_webhook, name='quickresto-webhook'),

    # Основные страницы
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path("promotions/", views.promotions, name="promotions"),

    # Заказ
    path("order/", views.make_order, name="make_order"),

    # Корзина
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/<int:item_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),

    # Авторизация
    path('accounts/login/', auth_views.LoginView.as_view(template_name='main/'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # История заказов
    path("orders/history/", views.order_history, name="order_history"),

    # Кабинет менеджера
    path("manager/orders/", views.manager_orders, name="manager_orders"),
    path("manager/orders/<int:order_id>/assign/", views.assign_courier, name="assign_courier"),
    path("manager/orders/<int:order_id>/status/", views.update_order_status, name="update_order_status"),

    # Кабинет курьера
    path("courier/orders/", views.courier_orders, name="courier_orders"),
    path("courier/orders/<int:order_id>/done/", views.courier_update_order, name="courier_update_order"),
    # Готовка
    path("kitchen/orders/", views.kitchen_orders, name="kitchen_orders"),
    path("kitchen/orders/<int:order_id>/cook/", views.kitchen_set_cooking, name="kitchen_set_cooking"),
    path("kitchen/orders/<int:order_id>/delivery/", views.kitchen_send_to_delivery, name="kitchen_send_to_delivery"),
    # Панель управления заказами
    path('orders/dashboard/', views.OrderDashboardView.as_view(), name='order_dashboard'),

    # API для комментариев (если нужно)
    path('orders/<int:order_id>/comment/', views.AddOrderCommentView.as_view(), name='add_order_comment'),
    path('api/sync-orders/', views.sync_quickresto_orders, name='sync-orders'),
    path('api/order-status/<str:order_id>/', views.get_order_status, name='order-status'),
    path('api/quickresto/', include('quickresto_api.urls')),
]
