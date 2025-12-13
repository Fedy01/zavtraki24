# management/commands/sync_quickresto.py
from django.core.management.base import BaseCommand
from app.services.sync_service import QuickRestoSyncService


class Command(BaseCommand):
    help = 'Синхронизация данных с Quick Resto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['products', 'orders', 'all'],
            default='all'
        )

    def handle(self, *args, **options):
        sync_service = QuickRestoSyncService()

        if options['type'] in ['products', 'all']:
            self.stdout.write('Синхронизация товаров...')
            if sync_service.sync_products():
                self.stdout.write('✓ Товары синхронизированы')
            else:
                self.stdout.write('✗ Ошибка синхронизации товаров')

        if options['type'] in ['orders', 'all']:
            self.stdout.write('Синхронизация заказов...')
            if sync_service.sync_orders():
                self.stdout.write('✓ Заказы синхронизированы')
            else:
                self.stdout.write('✗ Ошибка синхронизации заказов')