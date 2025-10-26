from django.shortcuts import render
from .models import MenuItem

def home(request):
    return render(request, "main/home.html")

def menu(request):
    items = MenuItem.objects.all()
    return render(request, "main/menu.html", {"items": items})

def promotions(request):
    return render(request, "main/promotions.html")