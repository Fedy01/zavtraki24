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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import QuickRestoOrder
from garbage.tasks import sync_orders_with_quickresto
import json
import hashlib
import hmac
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings

QR_STATUS_MAP = {
    'NEW': 'new',
    'CONFIRMED': 'confirmed',
    'COOKING': 'cooking',
    'READY': 'ready',
    'DONE': 'completed',
    'CANCELLED': 'cancelled',
}

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
    return render(request, "main/")

def menu(request):
    items = MenuItem.objects.all()
    return render(request, "main/", {"items": items})

def promotions(request):
    return render(request, "main/")


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

    return render(request, "main/", {
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

            return render(request, "main/", {"order": order})

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

    return render(request, "main/", {
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
    return render(request, "main/", {"orders": orders})


# ─────────────────────────────────────
# КАБИНЕТ МЕНЕДЖЕРА
# ─────────────────────────────────────

@manager_required
def manager_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "main/", {"orders": orders})


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

    return render(request, "main/", {
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

    return render(request, "main/", {
        "order": order,
        "couriers": couriers
    })


# ─────────────────────────────────────
# КАБИНЕТ КУРЬЕРА
# ─────────────────────────────────────

@courier_required
def courier_orders(request):
    orders = Order.objects.filter(courier=request.user).order_by("-created_at")
    return render(request, "main/", {"orders": orders})


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
    return render(request, "main/", {"orders": orders})

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
    template_name = 'orders/'

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
    """Webhook от QuickResto"""
    try:
        signature = request.headers.get('X-QuickResto-Signature')
        if not signature:
            return JsonResponse({'error': 'Missing signature'}, status=400)

        body = request.body.decode('utf-8')
        expected_signature = hmac.new(
            settings.QUICKRESTO_API_SECRET.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        if signature != expected_signature:
            return JsonResponse({'error': 'Invalid signature'}, status=403)

        payload = json.loads(body)
        event = payload.get('event')
        order_data = payload.get('data', {})

        if event in ('order.created', 'order.updated'):
            return upsert_quickresto_order(order_data)

        if event == 'order.status_changed':
            return update_quickresto_status(order_data)

        return JsonResponse({'status': 'ignored'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def upsert_quickresto_order(order_data):
        order_id = order_data.get('id')
        if not order_id:
            return JsonResponse({'error': 'Missing order ID'}, status=400)

        status = QR_STATUS_MAP.get(order_data.get('status'), 'new')

        order, created = QuickRestoOrder.objects.update_or_create(
            quickresto_id=str(order_id),
            defaults={
                'order_number': order_data.get('number', ''),
                'table_name': order_data.get('tableName', ''),
                'customer_name': order_data.get('customerName', ''),
                'customer_phone': order_data.get('customerPhone', ''),
                'total_amount': order_data.get('totalAmount', 0),
                'status': status,
                'quickresto_data': order_data,
                'created_at': order_data.get('createdAt', timezone.now()),
            }
        )

        return JsonResponse({
            'status': 'success',
            'created': created,
            'quickresto_id': order.quickresto_id
        })

def update_quickresto_status(order_data):
        order_id = order_data.get('id')
        new_status = order_data.get('status')

        if not order_id or not new_status:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        status = QR_STATUS_MAP.get(new_status, 'new')

        try:
            order = QuickRestoOrder.objects.get(quickresto_id=str(order_id))
            order.status = status
            order.save(update_fields=['status'])

            return JsonResponse({'status': 'success'})

        except QuickRestoOrder.DoesNotExist:
            return upsert_quickresto_order(order_data)

@csrf_exempt
@require_POST
def sync_quickresto_orders(request):
    """Ручной запуск синхронизации"""
    auth = request.headers.get('Authorization')

    # ⚠️ ВРЕМЕННО, НЕ ПРОД
    if auth != f"Bearer {settings.QUICKRESTO_API_KEY}":
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    task = sync_orders_with_quickresto.delay()
    return JsonResponse({'status': 'started', 'task_id': task.id})

def get_order_status(request, order_id):
    try:
        order = QuickRestoOrder.objects.get(quickresto_id=str(order_id))
        return JsonResponse({
            'order_number': order.order_number,
            'status': order.status,
            'total': str(order.total_amount),
            'created_at': order.created_at.isoformat()
        })
    except QuickRestoOrder.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
