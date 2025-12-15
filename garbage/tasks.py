from celery import shared_task
from django.utils import timezone
from django.conf import settings
from garbage.quickresto_api import QuickRestoAPI
from main.models import QuickRestoOrder, QuickRestoMenuItem
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_orders_with_quickresto():
    """Синхронизация заказов с QuickResto"""
    api = QuickRestoAPI(
        api_key=settings.QUICKRESTO_API_KEY,
        api_secret=settings.QUICKRESTO_API_SECRET
    )

    # Получаем заказы за последние 24 часа
    date_from = (timezone.now() - timezone.timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        orders_data = api.get_orders(date_from=date_from)

        if orders_data and 'orders' in orders_data:
            for order_data in orders_data['orders']:
                order_id = order_data.get('id')

                # Получаем детальную информацию о заказе
                detailed_order = api.get_order_by_id(order_id)

                if detailed_order:
                    order, created = QuickRestoOrder.objects.update_or_create(
                        quickresto_id=order_id,
                        defaults={
                            'order_number': detailed_order.get('number', ''),
                            'table_name': detailed_order.get('tableName', ''),
                            'customer_name': detailed_order.get('customerName', ''),
                            'customer_phone': detailed_order.get('customerPhone', ''),
                            'total_amount': detailed_order.get('totalAmount', 0),
                            'status': detailed_order.get('status', 'new'),
                            'created_at': timezone.now(),
                            'quickresto_data': detailed_order
                        }
                    )

                    if created:
                        logger.info(f"Создан новый заказ: {order.order_number}")
                    else:
                        logger.info(f"Обновлен заказ: {order.order_number}")

    except Exception as e:
        logger.error(f"Ошибка синхронизации заказов: {e}")


@shared_task
def sync_menu_with_quickresto():
    """Синхронизация меню с QuickResto"""
    api = QuickRestoAPI(
        api_key=settings.QUICKRESTO_API_KEY,
        api_secret=settings.QUICKRESTO_API_SECRET
    )

    try:
        menu_items = api.get_menu_items()

        if menu_items:
            for item in menu_items:
                item_id = item.get('id')

                menu_item, created = QuickRestoMenuItem.objects.update_or_create(
                    quickresto_id=item_id,
                    defaults={
                        'name': item.get('name', ''),
                        'category_name': item.get('categoryName', ''),
                        'price': item.get('price', 0),
                        'description': item.get('description', ''),
                        'is_active': item.get('isActive', True)
                    }
                )

    except Exception as e:
        logger.error(f"Ошибка синхронизации меню: {e}")