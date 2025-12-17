# main/management/commands/sync_customers.py
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth


class Command(BaseCommand):
    help = "Синхронизация клиентов с Quick Resto API"

    def handle(self, *args, **options):
        # Проверка настроек
        api_config = getattr(settings, "QUICK_RESTO_API", None)
        if not api_config:
            self.stdout.write(self.style.ERROR("Настройки QUICK_RESTO_API не найдены"))
            return

        layer_name = api_config.get("LAYER_NAME", "default")
        self.stdout.write(f"Использую настройки для слоя: {layer_name}")

        # Формируем URL и авторизацию
        base_url = api_config["BASE_URL"].format(layer_name=layer_name)
        auth = HTTPBasicAuth(api_config["USERNAME"], api_config["PASSWORD"])

        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
        }

        endpoint = "/bonuses/filterCustomers"
        url = f"{base_url}{endpoint}"

        payload = {
            "search": "",
            "typeList": ["customer"],
            "limit": 10,
            "offset": 0,
        }

        try:
            response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            customers = result.get("items", [])
            customers_count = len(customers)

            self.stdout.write(
                self.style.SUCCESS(f"Успешно подключились к API. Найдено клиентов: {customers_count}")
            )

            # Вывод первых 3 клиентов
            for i, customer in enumerate(customers[:3], start=1):
                last_name = customer.get("lastName", "")
                first_name = customer.get("firstName", "")
                self.stdout.write(f"{i}. {last_name} {first_name}")

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Ошибка подключения к API: {e}"))
            self.stdout.write(f"URL: {url}")
            self.stdout.write(f"Username: {api_config['USERNAME'][:5]}...")
