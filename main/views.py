from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View

from .models import MenuItem, Order, OrderItem, OrderComment
from .forms import OrderForm
from .decorators import manager_required, courier_required

from .utils import notify_new_order
from .decorators import kitchen_required




# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# import json
# import hashlib
# import hmac
# from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import QuickRestoOrder
from garbage.tasks import sync_orders_with_quickresto
import json
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone



CART_SESSION_ID = "cart"


# ─────────────────────────────────────
# КОРЗИНА
# ─────────────────────────────────────

def _get_cart(request):
    return request.session.get(CART_SESSION_ID, {})

def _save_cart(request, cart):
    request.session[CART_SESSION_ID] = cart
    request.session.modified = True


# ─────────────────────────────────────
# ПУБЛИЧНЫЕ СТРАНИЦЫ
# ─────────────────────────────────────

def home(request):
    return render(request, "main/home.html")

def menu(request):
    items = MenuItem.objects.all()
    return render(request, "main/menu.html", {"items": items})

def promotions(request):
    return render(request, "main/promotions.html")


# ─────────────────────────────────────
# КОРЗИНА СТР
# ─────────────────────────────────────

def add_to_cart(request, item_id):
    if request.method != "POST":
        return redirect("menu")

    qty = int(request.POST.get("qty", 1))
    mi = get_object_or_404(MenuItem, pk=item_id)

    cart = _get_cart(request)
    cart[str(item_id)] = cart.get(str(item_id), 0) + qty
    _save_cart(request, cart)

    return redirect("view_cart")

def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    cart.pop(str(item_id), None)
    _save_cart(request, cart)
    return redirect("view_cart")

def view_cart(request):
    cart = _get_cart(request)
    items = []
    total = 0

    for sid, qty in cart.items():
        mi = MenuItem.objects.filter(pk=int(sid)).first()
        if not mi:
            continue
        items.append({"item": mi, "qty": qty, "sum": mi.price * qty})
        total += mi.price * qty

    return render(request, "main/cart.html", {
        "cart_items": items,
        "total": total
    })


# ─────────────────────────────────────
# ОФОРМЛЕНИЕ ЗАКАЗА
# ─────────────────────────────────────

def make_order(request):
    cart = _get_cart(request)
    if not cart:
        return redirect("menu")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user

            order.save()

            # сохранить позиции
            for sid, qty in cart.items():
                mi = MenuItem.objects.filter(pk=int(sid)).first()
                if mi:
                    OrderItem.objects.create(
                        order=order, item=mi, quantity=qty
                    )
            # отправка уведомления админу
            notify_new_order(order)

            # очистить корзину
            request.session[CART_SESSION_ID] = {}
            request.session.modified = True

            # отправка телеграм уведомления
            try:
                from .utils import send_order_notification
                send_order_notification(order)
            except Exception as e:
                print("Telegram notify failed:", e)

            return render(request, "main/order_success.html", {"order": order})

    else:
        form = OrderForm()

    # показать корзину на странице оформления
    items = []
    total = 0
    for sid, qty in cart.items():
        mi = MenuItem.objects.filter(pk=int(sid)).first()
        if mi:
            items.append({"item": mi, "qty": qty, "sum": mi.price * qty})
            total += mi.price * qty

    return render(request, "main/make_order.html", {
        "form": form,
        "cart_items": items,
        "total": total
    })


# ─────────────────────────────────────
# ИСТОРИЯ ЗАКАЗОВ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
# ─────────────────────────────────────

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "main/order_history.html", {"orders": orders})


# ─────────────────────────────────────
# КАБИНЕТ МЕНЕДЖЕРА
# ─────────────────────────────────────

@manager_required
def manager_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "main/manager_orders.html", {"orders": orders})


@manager_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        order.status = new_status
        order.save()

        from .utils import notify_client
        notify_client(order, f"Ваш заказ #{order.id} теперь: {order.get_status_display()}")

        return redirect("manager_orders")

    return render(request, "main/update_order_status.html", {
        "order": order,
        "statuses": Order.STATUS_CHOICES,
    })


@manager_required
def assign_courier(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    couriers = User.objects.filter(groups__name="courier")

    if request.method == "POST":
        order.courier_id = request.POST.get("courier_id")
        order.save()
        return redirect("manager_orders")

    return render(request, "main/assign_courier.html", {
        "order": order,
        "couriers": couriers
    })


# ─────────────────────────────────────
# КАБИНЕТ КУРЬЕРА
# ─────────────────────────────────────

@courier_required
def courier_orders(request):
    orders = Order.objects.filter(courier=request.user).order_by("-created_at")
    return render(request, "main/courier_orders.html", {"orders": orders})


@courier_required
def courier_update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, courier=request.user)

    if order.status == "DELIVERY":
        order.status = "DONE"
        order.save()

        from .utils import notify_client
        notify_client(order, "Ваш заказ доставлен! Спасибо за покупку ❤️")

    return redirect("courier_orders")

@kitchen_required
def kitchen_orders(request):
    orders = Order.objects.filter(status__in=["NEW", "COOKING"]).order_by("created_at")
    return render(request, "main/kitchen_orders.html", {"orders": orders})

@kitchen_required
def kitchen_set_cooking(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "COOKING"
    order.save()

    from .utils import notify_client
    notify_client(order, f"Ваш заказ #{order.id} начали готовить 🔥")

    return redirect("kitchen_orders")

@kitchen_required
def kitchen_send_to_delivery(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "DELIVERY"
    order.save()

    from .utils import notify_client
    notify_client(order, f"Ваш заказ #{order.id} передан курьеру 🚗")

    return redirect("kitchen_orders")


@csrf_exempt
def quickresto_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_type = data.get('event')

            if event_type == 'order.created':
                # Обработка нового заказа
                order_data = data.get('data')
                # Сохранение в вашей БД

            elif event_type == 'order.updated':
                # Обновление статуса заказа
                pass

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=405)


# views.py - Dashboard для отслеживания заказов
class OrderDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Группировка заказов по статусам
        context['new_orders'] = Order.objects.filter(status='NEW')
        context['preparing_orders'] = Order.objects.filter(status='READY_FOR_PACKING')
        context['on_the_way_orders'] = Order.objects.filter(status='ON_THE_WAY')
        context['delivered_orders'] = Order.objects.filter(status='DELIVERED')

        return context


class AddOrderCommentView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        comment_text = request.POST.get('comment')

        comment = OrderComment.objects.create(
            order=order,
            author=request.user,
            comment=comment_text,
            is_internal=request.POST.get('is_internal') == 'true'
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'text': comment.comment,
                'author': comment.author.get_full_name(),
                'created_at': comment.created_at.strftime('%H:%M')
            }
        })





@csrf_exempt
@require_POST
def quickresto_webhook(request):
    """Обработка вебхуков от QuickResto"""
    try:
        # Получаем подпись из заголовков
        signature = request.headers.get('X-QuickResto-Signature')

        if not signature:
            return JsonResponse({'error': 'Missing signature'}, status=400)

        # Проверяем подпись
        body = request.body.decode('utf-8')
        expected_signature = hmac.new(
            settings.QUICKRESTO_API_SECRET.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if signature != expected_signature:
            return JsonResponse({'error': 'Invalid signature'}, status=403)

        data = json.loads(body)
        event_type = data.get('event')
        order_data = data.get('data', {})

        # Обработка различных событий
        if event_type == 'order.created':
            return handle_new_order(order_data)
        elif event_type == 'order.updated':
            return handle_order_update(order_data)
        elif event_type == 'order.status_changed':
            return handle_order_status_change(order_data)
        else:
            # Неизвестное событие, просто подтверждаем получение
            return JsonResponse({'status': 'received'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def handle_new_order(order_data):
    """Обработка нового заказа"""
    try:
        order_id = order_data.get('id')

        if not order_id:
            return JsonResponse({'error': 'Missing order ID'}, status=400)

        # Создаем или обновляем заказ в базе данных
        order, created = QuickRestoOrder.objects.update_or_create(
            quickresto_id=order_id,
            defaults={
                'order_number': order_data.get('number', ''),
                'table_name': order_data.get('tableName', ''),
                'customer_name': order_data.get('customerName', ''),
                'customer_phone': order_data.get('customerPhone', ''),
                'total_amount': order_data.get('totalAmount', 0),
                'status': order_data.get('status', 'new'),
                'created_at': timezone.now(),
                'quickresto_data': order_data
            }
        )

        action = 'created' if created else 'updated'
        return JsonResponse({
            'status': 'success',
            'message': f'Order {action} successfully',
            'order_id': str(order.id),
            'quickresto_id': order.quickresto_id
        })

    except Exception as e:
        return JsonResponse({'error': f'Failed to process order: {str(e)}'}, status=500)


def handle_order_update(order_data):
    """Обработка обновления заказа"""
    try:
        order_id = order_data.get('id')

        if not order_id:
            return JsonResponse({'error': 'Missing order ID'}, status=400)

        # Обновляем заказ в базе данных
        order, created = QuickRestoOrder.objects.update_or_create(
            quickresto_id=order_id,
            defaults={
                'order_number': order_data.get('number', ''),
                'table_name': order_data.get('tableName', ''),
                'customer_name': order_data.get('customerName', ''),
                'customer_phone': order_data.get('customerPhone', ''),
                'total_amount': order_data.get('totalAmount', 0),
                'status': order_data.get('status', 'new'),
                'created_at': timezone.now(),
                'quickresto_data': order_data
            }
        )

        action = 'created' if created else 'updated'
        return JsonResponse({
            'status': 'success',
            'message': f'Order {action} successfully',
            'order_id': str(order.id),
            'quickresto_id': order.quickresto_id
        })

    except Exception as e:
        return JsonResponse({'error': f'Failed to update order: {str(e)}'}, status=500)


def handle_order_status_change(order_data):
    """Обработка изменения статуса заказа"""
    try:
        order_id = order_data.get('id')
        new_status = order_data.get('status')

        if not order_id:
            return JsonResponse({'error': 'Missing order ID'}, status=400)
        if not new_status:
            return JsonResponse({'error': 'Missing new status'}, status=400)

        # Находим заказ и обновляем статус
        try:
            order = QuickRestoOrder.objects.get(quickresto_id=order_id)
            old_status = order.status
            order.status = new_status
            order.save(update_fields=['status'])

            # Можно добавить логирование изменения статуса
            print(f"Order {order_id}: status changed from {old_status} to {new_status}")

            return JsonResponse({
                'status': 'success',
                'message': 'Order status updated successfully',
                'order_id': str(order.id),
                'quickresto_id': order.quickresto_id,
                'old_status': old_status,
                'new_status': new_status
            })

        except QuickRestoOrder.DoesNotExist:
            # Если заказа нет в базе, создаем его
            return handle_new_order(order_data)

    except Exception as e:
        return JsonResponse({'error': f'Failed to change order status: {str(e)}'}, status=500)


# Дополнительный endpoint для ручной синхронизации
@csrf_exempt
@require_POST
def sync_quickresto_orders(request):
    """Ручная синхронизация заказов"""
    try:
        # Проверка авторизации (добавьте свою логику)
        auth_token = request.headers.get('Authorization')
        if not auth_token or auth_token != f"Bearer {settings.QUICKRESTO_API_KEY}":
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Запускаем синхронизацию
        result = sync_orders_with_quickresto.delay()  # Асинхронно через Celery

        return JsonResponse({
            'status': 'success',
            'message': 'Sync started',
            'task_id': result.id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Endpoint для проверки статуса заказа
def get_order_status(request, order_id):
    """Получение статуса заказа"""
    try:
        order = QuickRestoOrder.objects.get(quickresto_id=order_id)

        return JsonResponse({
            'status': 'success',
            'order_id': order.quickresto_id,
            'order_number': order.order_number,
            'status': order.status,
            'customer_name': order.customer_name,
            'total_amount': str(order.total_amount),
            'created_at': order.created_at.isoformat()
        })

    except QuickRestoOrder.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# main/views.py - добавьте эту функцию
from django.http import JsonResponse
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth


def test_quickresto_api(request):
    """Тестовый endpoint для проверки подключения к Quick Resto"""
    try:
        api_config = settings.QUICK_RESTO_API

        base_url = api_config['BASE_URL'].format(
            layer_name=api_config['LAYER_NAME']
        )
        auth = HTTPBasicAuth(
            api_config['USERNAME'],
            api_config['PASSWORD']
        )

        headers = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        }

        # Тестовый запрос - получение единиц измерения
        url = f"{base_url}/api/list?moduleName=core.dictionaries.measureunits&className=ru.edgex.quickresto.modules.core.dictionaries.measureunits.MeasureUnit"

        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        return JsonResponse({
            'status': 'success',
            'message': 'Подключение к Quick Resto API успешно',
            'data_count': len(data),
            'first_item': data[0] if data else None
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'config': {
                'base_url': api_config['BASE_URL'],
                'layer_name': api_config['LAYER_NAME'],
                'username': api_config['USERNAME'][:5] + '...'
            }
        }, status=500)