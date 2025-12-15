# quickresto_api/services.py
from .clients import QuickRestoClient
from django.core.cache import cache


class QuickRestoService:
    def __init__(self):
        self.client = QuickRestoClient()

    def search_customers(self, query, limit=50):
        """Поиск клиентов с кэшированием"""
        cache_key = f"quickresto_customers_{query}_{limit}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        result = self.client.filter_customers(
            search=query,
            limit=limit
        )

        # Кэшируем на 5 минут
        cache.set(cache_key, result, 300)
        return result

    def get_customer_details(self, customer_guid):
        """Получение детальной информации о клиенте"""
        return self.client.get_customer(customer_guid)

    def update_customer_address(self, customer_guid, address_data):
        """Обновление адреса клиента"""
        # Сначала получаем текущие данные
        customer = self.get_customer_details(customer_guid)

        # Обновляем адрес
        customer['addresses'] = [address_data]

        return self.client.put_customer(customer)

    def get_businesses(self):
        """Получение списка организаций"""
        return self.client.list_objects(
            module_name='core.company.businesses',
            class_name='ru.edgex.quickresto.modules.core.company.businesses.Business'
        )

    def get_measure_units(self):
        """Получение единиц измерения"""
        return self.client.list_objects(
            module_name='core.dictionaries.measureunits',
            class_name='ru.edgex.quickresto.modules.core.dictionaries.measureunits.MeasureUnit'
        )