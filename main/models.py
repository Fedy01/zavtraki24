from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# =========================
# БАЗОВЫЕ МОДЕЛИ
# =========================

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


# =========================
# ЗАКАЗЫ (ВНУТРЕННИЕ)
# =========================

class Order(models.Model):
    STATUS_CHOICES = [
        ("NEW", "Создан"),
        ("COOKING", "Готовится"),
        ("DELIVERY", "В пути"),
        ("DONE", "Доставлен"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    courier = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="deliveries",
        on_delete=models.SET_NULL,
        verbose_name="Курьер"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW"
    )
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} × {self.quantity}"


class OrderComment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий к заказу #{self.order.id}"


# =========================
# МАГАЗИН / СКЛАД
# =========================

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StoreProduct(models.Model):
    PRODUCT_UNITS = [
        ('kg', 'Килограмм'),
        ('g', 'Грамм'),
        ('l', 'Литр'),
        ('ml', 'Миллилитр'),
        ('piece', 'Штука'),
        ('pack', 'Упаковка'),
        ('portion', 'Порция'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=PRODUCT_UNITS, default='portion')
    in_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Promotion(models.Model):
    PROMOTION_TYPES = [
        ('percentage', 'Процент'),
        ('fixed', 'Фиксированная сумма'),
        ('bogo', 'Купи 1 получи 2'),
    ]

    name = models.CharField(max_length=200)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(StoreProduct, blank=True)
    categories = models.ManyToManyField(ProductCategory, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# QUICK RESTO (ИНТЕГРАЦИЯ)
# =========================

class QuickRestoProduct(models.Model):
    quickresto_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class QuickRestoMenuItem(models.Model):
    quickresto_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    category_name = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class QuickRestoOrder(models.Model):
    ORDER_STATUS = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('cooking', 'Готовится'),
        ('ready', 'Готов'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    quickresto_id = models.CharField(max_length=100, unique=True)
    order_number = models.CharField(max_length=50)
    table_name = models.CharField(max_length=200, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    quickresto_data = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ {self.order_number}"
