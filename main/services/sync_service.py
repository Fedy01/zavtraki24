# services/sync_service.py
from django.utils import timezone
from .quickresto_client import QuickRestoAPI
from django.conf import settings
from ..models import QuickRestoProduct, QuickRestoOrder


class QuickRestoSyncService:
    def __init__(self):
        config = settings.QUICK_RESTO
        self.api = QuickRestoAPI(
            login=config['LOGIN'],
            password=config['PASSWORD'],
            company_id=config['COMPANY_ID']
        )

    def sync_products(self):
        """Синхронизация товаров"""
        try:
            products_data = self.api.get_products()

            for item in products_data.get('list', []):
                product, created = QuickRestoProduct.objects.update_or_create(
                    qr_id=str(item['id']),
                    defaults={
                        'name': item.get('name', ''),
                        'price': item.get('salePrice', 0),
                        'category': item.get('category', {}).get('name', ''),
                        'is_active': item.get('active', True)
                    }
                )
            return True
        except Exception as e:
            print(f"Sync error: {e}")
            return False

    def sync_orders(self, date_from=None):
        """Синхронизация заказов"""
        try:
            # Можно добавить фильтрацию по дате
            orders_data = self.api.get_orders()

            for order in orders_data.get('list', []):
                QuickRestoOrder.objects.update_or_create(
                    qr_id=str(order['id']),
                    defaults={
                        'order_number': order.get('number', ''),
                        'status': self._map_status(order.get('state')),
                        'total_amount': order.get('total', 0),
                        'created_at': order.get('createDate', timezone.now()),
                        'items': order.get('items', [])
                    }
                )
            return True
        except Exception as e:
            print(f"Orders sync error: {e}")
            return False

    def _map_status(self, qr_status):
        """Маппинг статусов Quick Resto на локальные"""
        status_map = {
            'NEW': 'new',
            'CONFIRMED': 'confirmed',
            'DONE': 'completed',
            'CANCELLED': 'cancelled'
        }
        return status_map.get(qr_status, 'new')