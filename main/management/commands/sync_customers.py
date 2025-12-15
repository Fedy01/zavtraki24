# main/management/commands/sync_customers.py
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
import json


class Command(BaseCommand):
    help = 'Синхронизация клиентов с Quick Resto API'

    def handle(self, *args, **options):
        # Проверяем настройки
        if not hasattr(settings, 'QUICK_RESTO_API'):
            self.stdout.write(self.style.ERROR('Настройки QUICK_RESTO_API не найдены'))
            return

        api_config = settings.QUICK_RESTO_API
        self.stdout.write(f"Использую настройки для: {api_config.get('LAYER_NAME')}")

        # Создаем клиент
        base_url = api_config['BASE_URL'].format(
            layer_name=api_config['LAYER_NAME']
        )
        auth = HTTPBasicAuth(
            api_config['USERNAME'],
            api_config['PASSWORD']
        )

        headers = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        }

        # Тестовый запрос
        endpoint = "/bonuses/filterCustomers"
        url = f"{base_url}{endpoint}"

        data = {
            "search": "",
            "typeList": ["customer"],
            "limit": 10,
            "offset": 0
        }

        try:
            response = requests.post(
                url,
                auth=auth,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            customers_count = len(result.get('items', []))

            self.stdout.write(self.style.SUCCESS(
                f'Успешно подключились к API. Найдено клиентов: {customers_count}'
            ))

            # Выводим первых 3 клиента для примера
            for i, customer in enumerate(result.get('items', [])[:3]):
                self.stdout.write(f"{i + 1}. {customer.get('lastName', '')} {customer.get('firstName', '')}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
            self.stdout.write(f"URL: {url}")
            self.stdout.write(f"Username: {api_config['USERNAME'][:5]}...")