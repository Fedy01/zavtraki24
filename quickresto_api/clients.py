# quickresto_api/clients.py
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
import json


class QuickRestoClient:
    def __init__(self):
        self.base_url = settings.QUICK_RESTO_API['BASE_URL'].format(
            layer_name=settings.QUICK_RESTO_API['LAYER_NAME']
        )
        self.auth = HTTPBasicAuth(
            settings.QUICK_RESTO_API['USERNAME'],
            settings.QUICK_RESTO_API['PASSWORD']
        )
        self.session = requests.Session()
        self.session.auth = self.auth
        self.timeout = settings.QUICK_RESTO_API.get('TIMEOUT', 30)

        # Заголовки по умолчанию
        self.headers = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        }

    def _make_request(self, method, endpoint, **kwargs):
        """Базовый метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"

        # Добавляем заголовки
        kwargs.setdefault('headers', {}).update(self.headers)
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Логирование ошибки
            print(f"Quick Resto API error: {e}")
            raise

    # CRM методы
    def filter_customers(self, search, limit=150, offset=0):
        """Поиск клиентов"""
        endpoint = "/bonuses/filterCustomers"
        data = {
            "search": search,
            "typeList": ["customer"],
            "limit": limit,
            "offset": offset
        }
        return self._make_request('POST', endpoint, json=data)

    def get_customer(self, customer_guid):
        """Получить информацию о клиенте"""
        endpoint = "/bonuses/getCustomer"
        data = {"customerGuid": customer_guid}
        return self._make_request('POST', endpoint, json=data)

    def put_customer(self, customer_data):
        """Редактировать клиента"""
        endpoint = "/bonuses/putCustomer"
        return self._make_request('POST', endpoint, json=customer_data)

    def authorize_customer(self, customer_token, type_list=None):
        """Авторизация клиента"""
        endpoint = "/bonuses/authorizeCustomer"
        data = {
            "customerToken": customer_token
        }
        if type_list:
            data["typeList"] = type_list
        return self._make_request('POST', endpoint, json=data)

    def get_customer_balance(self, customer_token, account_guid):
        """Баланс бонусного счета"""
        endpoint = "/bonuses/balance"
        data = {
            "customerToken": customer_token,
            "accountType": {"accountGuid": account_guid}
        }
        return self._make_request('POST', endpoint, json=data)

    # CRUD операции для справочников
    def read_object(self, module_name, class_name, object_id):
        """Чтение объекта"""
        endpoint = f"/api/read?moduleName={module_name}&className={class_name}"
        params = {"objectId": object_id}
        return self._make_request('GET', endpoint, params=params)

    def list_objects(self, module_name, class_name, **filters):
        """Список объектов"""
        endpoint = f"/api/list?moduleName={module_name}&className={class_name}"
        return self._make_request('GET', endpoint, params=filters)

    def create_object(self, module_name, class_name, data):
        """Создание объекта"""
        endpoint = f"/api/create?moduleName={module_name}&className={class_name}"
        return self._make_request('POST', endpoint, json=data)

    def update_object(self, module_name, class_name, data):
        """Обновление объекта"""
        endpoint = f"/api/update?moduleName={module_name}&className={class_name}"
        return self._make_request('POST', endpoint, json=data)

    def remove_object(self, module_name, class_name, object_id):
        """Удаление объекта"""
        endpoint = f"/api/remove?moduleName={module_name}&className={class_name}"
        data = {"id": object_id}
        return self._make_request('POST', endpoint, json=data)