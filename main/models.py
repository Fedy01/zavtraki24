# from django.contrib.auth.models import User
# from django.db import models
# from django.utils import timezone
#
#
# class Table(models.Model):
#     name = models.CharField(max_length=100)
#     seats_count = models.PositiveIntegerField(default=4)
#
#     def __str__(self):
#         return f"{self.name} ({self.seats_count})"
#
#
# class MenuItem(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#
#     def __str__(self):
#         return self.name
#
#
# class Order(models.Model):
#     STATUS_CHOICES = [
#         ("NEW", "Создан"),
#         ("COOKING", "Готовится"),
#         ("DELIVERY", "В пути"),
#         ("DONE", "Доставлен"),
#     ]
#
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         verbose_name="Пользователь",
#     )
#     courier = models.ForeignKey(
#         User,
#         null=True,
#         blank=True,
#         related_name="deliveries",
#         on_delete=models.SET_NULL,
#         verbose_name="Курьер"
#     )
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW", verbose_name="Статус")
#     created_at = models.DateTimeField(default=timezone.now, verbose_name="Время создания")
#     name = models.CharField(max_length=100, verbose_name="Имя клиента")
#     phone = models.CharField(max_length=20, verbose_name="Телефон")
#     address = models.CharField(max_length=255, verbose_name="Адрес доставки", blank=True)
#     comment = models.TextField(verbose_name="Комментарий", blank=True)
#     telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
#
#     def __str__(self):
#         return f"Заказ #{self.id} от {self.name}"
#
#     class Meta:
#         verbose_name = "Заказ"
#         verbose_name_plural = "Заказы"
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
#     item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#
#     def __str__(self):
#         return f"{self.item.name} × {self.quantity}"
#
#     class Meta:
#         verbose_name = "Позиция заказа"
#         verbose_name_plural = "Позиции заказа"
#
#
#
#
# class QuickRestoProduct(models.Model):
#     qr_id = models.CharField(max_length=100, unique=True)
#     name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     category = models.CharField(max_length=255, null=True)
#     is_active = models.BooleanField(default=True)
#     last_sync = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.name
#
#
# class QuickRestoOrder(models.Model):
#     STATUS_CHOICES = [
#         ('new', 'Новый'),
#         ('confirmed', 'Подтвержден'),
#         ('completed', 'Выполнен'),
#         ('cancelled', 'Отменен'),
#     ]
#
#     qr_id = models.CharField(max_length=100, unique=True)
#     order_number = models.CharField(max_length=50)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField()
#     items = models.JSONField(default=list)
#
#     def __str__(self):
#         return f"Order {self.order_number}"
#
#     # models.py
#     class OrderComment(models.Model):
#         order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
#         author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#         comment = models.TextField()
#         created_at = models.DateTimeField(auto_now_add=True)
#         is_internal = models.BooleanField(default=False)  # Для внутренних заметок
#
#         class Meta:
#             ordering = ['-created_at']
#
#
# # models.py
# class Promotion(models.Model):
#     PROMOTION_TYPES = [
#         ('percentage', 'Процент'),
#         ('fixed', 'Фиксированная сумма'),
#         ('bogo', 'Купи 1 получи 2'),
#     ]
#
#     name = models.CharField(max_length=200)
#     promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
#     value = models.DecimalField(max_digits=10, decimal_places=2)
#     products = models.ManyToManyField('StoreProduct', blank=True)
#     categories = models.ManyToManyField('ProductCategory', blank=True)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     is_active = models.BooleanField(default=True)
#     min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#
#     def apply_to_order(self, order):
#         # Логика применения скидки
#         pass
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW", verbose_name="Статус")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Время создания")
    name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адрес доставки", blank=True)
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)

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


# Модель для комментариев к заказам - ВЫНЕСИТЕ ЕЕ ОТДЕЛЬНО
class OrderComment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)  # Для внутренних заметок

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on order #{self.order.id}"


# Сначала определите ProductCategory
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Потом StoreProduct
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
    min_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=10)
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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Только потом Promotion
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
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def apply_to_order(self, order):
        # Логика применения скидки
        pass


class QuickRestoProduct(models.Model):
    qr_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class QuickRestoOrder(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    qr_id = models.CharField(max_length=100, unique=True)
    order_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    items = models.JSONField(default=list)

    def __str__(self):
        return f"Order {self.order_number}"