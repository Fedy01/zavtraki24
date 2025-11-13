from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Table(models.Model):
    name = models.CharField(max_length=100)
    seats_count = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.name} ({self.seats_count})"


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Время создания")
    name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адрес доставки", blank=True)
    comment = models.TextField(verbose_name="Комментарий", blank=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} × {self.quantity}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
