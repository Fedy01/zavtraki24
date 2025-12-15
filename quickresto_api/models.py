from django.db import models

# Create your models here.
# quickresto_api/models.py
from django.db import models


class CachedCustomer(models.Model):
    """Локальная копия данных клиента"""
    guid = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_sync = models.DateTimeField(auto_now=True)
    raw_data = models.JSONField()  # Полные данные из API

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"