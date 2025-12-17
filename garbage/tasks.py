from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

from garbage.quickresto_api import QuickRestoAPI
from main.models import QuickRestoOrder, QuickRestoMenuItem

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def sync_orders_with_quickresto(self):
    """Синхронизация заказов с QuickResto"""
    api = QuickRestoAPI()

    date_from = (timezone.now() - timezone.timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        orders_data = api.get_orders(date_from=date_from)

        if not orders_data or "orders" not in orders_data:
            logger.info("Нет заказов для синхронизации")
            return

        with transaction.atomic():
            for order_data in orders_data["orders"]:
                order_id = order_data.get("id")
                if not order_id:
                    continue

                detailed_order = api.get_order_by_id(order_id)
                if not detailed_order:
                    continue

                order, created = QuickRestoOrder.objects.update_or_create(
                    quickresto_id=order_id,
                    defaults={
                        "order_number": detailed_order.get("number", ""),
                        "table_name": detailed_order.get("tableName", ""),
                        "customer_name": detailed_order.get("customerName", ""),
                        "customer_phone": detailed_order.get("customerPhone", ""),
                        "total_amount": detailed_order.get("totalAmount", 0),
                        "status": detailed_order.get("status", "new"),
                        "quickresto_data": detailed_order,
                    },
                )

                logger.info(
                    "Создан заказ %s" if created else "Обновлён заказ %s",
                    order.order_number,
                )

    except Exception:
        logger.exception("Ошибка синхронизации заказов")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def sync_menu_with_quickresto(self):
    """Синхронизация меню с QuickResto"""
    api = QuickRestoAPI()

    try:
        menu_items = api.get_menu_items()
        if not menu_items:
            logger.info("Меню пустое")
            return

        with transaction.atomic():
            for item in menu_items:
                item_id = item.get("id")
                if not item_id:
                    continue

                QuickRestoMenuItem.objects.update_or_create(
                    quickresto_id=item_id,
                    defaults={
                        "name": item.get("name", ""),
                        "category_name": item.get("categoryName", ""),
                        "price": item.get("price", 0),
                        "description": item.get("description", ""),
                        "is_active": item.get("isActive", True),
                    },
                )

    except Exception:
        logger.exception("Ошибка синхронизации меню")
        raise
