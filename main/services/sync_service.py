# main/services/sync_service.py
from django.utils import timezone
from django.conf import settings

from .quickresto_client import QuickRestoAPI
from main.models import QuickRestoProduct, QuickRestoOrder


class QuickRestoSyncService:
    def __init__(self):
        config = settings.QUICK_RESTO

        self.api = QuickRestoAPI(
            login=config['LOGIN'],
            password=config['PASSWORD'],
            company_id=config['COMPANY_ID']
        )

    def sync_products(self) -> bool:
        """Синхронизация товаров"""
        try:
            products_data = self.api.get_products()
            items = products_data.get('list', [])

            for item in items:
                QuickRestoProduct.objects.update_or_create(
                    qr_id=str(item['id']),
                    defaults={
                        'name': item.get('name', ''),
                        'price': item.get('salePrice', 0),
                        'category': item.get('category', {}).get('name', ''),
                        'is_active': item.get('active', True),
                    }
                )
            return True

        except Exception as e:
            print(f"[QuickResto] Products sync error: {e}")
            return False

    def sync_orders(self) -> bool:
        """Синхронизация заказов"""
        try:
            orders_data = self.api.get_orders()
            orders = orders_data.get('list', [])

            for order in orders:
                QuickRestoOrder.objects.update_or_create(
                    qr_id=str(order['id']),
                    defaults={
                        'order_number': order.get('number', ''),
                        'status': self._map_status(order.get('state')),
                        'total_amount': order.get('total', 0),
                        'created_at': order.get('createDate', timezone.now()),
                        'items': order.get('items', []),
                    }
                )
            return True

        except Exception as e:
            print(f"[QuickResto] Orders sync error: {e}")
            return False

    def _map_status(self, qr_status: str) -> str:
        """Маппинг статусов Quick Resto"""
        return {
            'NEW': 'new',
            'CONFIRMED': 'confirmed',
            'DONE': 'completed',
            'CANCELLED': 'cancelled',
        }.get(qr_status, 'new')
