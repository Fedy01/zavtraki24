# quickresto_client.py
import requests
import base64
from django.conf import settings


class QuickRestoAPI:
    def __init__(self, login, password, company_id):
        self.base_url = "https://api.quickresto.ru"
        self.login = login
        self.password = password
        self.company_id = company_id
        self.auth_header = self._get_auth_header()

    def _get_auth_header(self):
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _make_request(self, endpoint, method='GET', data=None):
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': self.auth_header,
            'Content-Type': 'application/json'
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")

    # Пример методов
    def get_products(self):
        return self._make_request('/platform/online/list?module=warehouse.nomenclature')

    def get_orders(self):
        return self._make_request('/platform/online/list?module=front.orders')

    def create_order(self, order_data):
        return self._make_request('/platform/online/create?module=front.orders',
                                  method='POST', data=order_data)