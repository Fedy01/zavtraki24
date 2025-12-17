from django.core.management.base import BaseCommand
from main.services.sync_service import QuickRestoSyncService


class Command(BaseCommand):
    help = "Синхронизация данных с Quick Resto"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["products", "orders", "all"],
            default="all",
            help="Тип данных для синхронизации: products, orders или all",
        )

    def handle(self, *args, **options):
        sync_service = QuickRestoSyncService()
        sync_type = options.get("type", "all")

        try:
            if sync_type in ["products", "all"]:
                self.stdout.write("Синхронизация товаров...")
                success = sync_service.sync_products()
                if success:
                    self.stdout.write(self.style.SUCCESS("✓ Товары синхронизированы"))
                else:
                    self.stdout.write(self.style.ERROR("✗ Ошибка синхронизации товаров"))

            if sync_type in ["orders", "all"]:
                self.stdout.write("Синхронизация заказов...")
                success = sync_service.sync_orders()
                if success:
                    self.stdout.write(self.style.SUCCESS("✓ Заказы синхронизированы"))
                else:
                    self.stdout.write(self.style.ERROR("✗ Ошибка синхронизации заказов"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка во время синхронизации: {e}"))
