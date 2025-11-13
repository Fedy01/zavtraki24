from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import MenuItem, OrderItem


def home(request):
    return render(request, "main/home.html")


def menu(request):
    items = MenuItem.objects.all()
    return render(request, "main/menu.html", {"items": items})


def promotions(request):
    return render(request, "main/promotions.html")


def make_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            # позже добавим добавление OrderItem
            return render(request, "main/order_success.html", {"order": order})
    else:
        form = OrderForm()
    return render(request, "main/make_order.html", {"form": form})
