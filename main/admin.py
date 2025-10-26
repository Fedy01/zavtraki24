from django.contrib import admin
from .models import Table, MenuItem

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'seats_count')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')