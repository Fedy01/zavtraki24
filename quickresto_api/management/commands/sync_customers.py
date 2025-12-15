# quickresto_api/management/commands/sync_customers.py
from django.core.management.base import BaseCommand
from quickresto_api.services import QuickRestoService
from quickresto_api.models import CachedCustomer


class Command(BaseCommand):
    help = 'Синхронизация клиентов с Quick Resto API'

    def handle(self, *args, **options):
        service = QuickRestoService()

        # Поиск клиентов (например, пустая строка для получения всех)
        result = service.search_customers('', limit=1000)

        for customer_data in result.get('items', []):
            CachedCustomer.objects.update_or_create(
                guid=customer_data['guid'],
                defaults={
                    'first_name': customer_data.get('firstName'),
                    'last_name': customer_data.get('lastName'),
                    'raw_data': customer_data
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Синхронизировано клиентов: {len(result.get("items", []))}'))