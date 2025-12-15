import requests
import json
from datetime import datetime
import hashlib
import hmac


class QuickRestoAPI:
    def __init__(self, api_key, api_secret, base_url="https://api.quickresto.ru"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()

    def _generate_signature(self, params):
        """Генерация подписи для запроса"""
        param_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _make_request(self, endpoint, method='GET', data=None, params=None):
        """Базовый метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"

        # Базовые параметры
        request_params = {
            'key': self.api_key,
            'timestamp': int(datetime.now().timestamp())
        }

        # Добавляем переданные параметры
        if params:
            request_params.update(params)

        # Генерируем подпись
        request_params['signature'] = self._generate_signature(request_params)

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            if method == 'GET':
                response = self.session.get(
                    url,
                    params=request_params,
                    headers=headers,
                    timeout=30
                )
            elif method == 'POST':
                response = self.session.post(
                    url,
                    params=request_params,
                    json=data,
                    headers=headers,
                    timeout=30
                )
            elif method == 'PUT':
                response = self.session.put(
                    url,
                    params=request_params,
                    json=data,
                    headers=headers,
                    timeout=30
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    # Методы для работы с заказами
    def get_orders(self, date_from=None, date_to=None, status=None):
        """Получение списка заказов"""
        params = {}
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if status:
            params['status'] = status

        return self._make_request('/platform/orders', params=params)

    def get_order_by_id(self, order_id):
        """Получение заказа по ID"""
        return self._make_request(f'/platform/orders/{order_id}')

    def update_order_status(self, order_id, status):
        """Обновление статуса заказа"""
        data = {
            'status': status
        }
        return self._make_request(
            f'/platform/orders/{order_id}/status',
            method='PUT',
            data=data
        )

    # Методы для работы с меню
    def get_menu_items(self):
        """Получение списка блюд"""
        return self._make_request('/platform/menu/items')

    def get_categories(self):
        """Получение категорий меню"""
        return self._make_request('/platform/menu/categories')

    # Методы для работы со столами
    def get_tables(self):
        """Получение списка столов"""
        return self._make_request('/platform/tables')

    def get_table_status(self, table_id):
        """Получение статуса стола"""
        return self._make_request(f'/platform/tables/{table_id}/status')