from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from .models import MenuItem, Order, OrderItem
from .forms import OrderForm
from .decorators import manager_required, courier_required

from .utils import notify_new_order
from .decorators import kitchen_required

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