# quickresto_client.py
import base64
import requests
from django.conf import settings


class QuickRestoAPI:
    BASE_URL = "https://api.quickresto.ru"
    TIMEOUT = 20

    def __init__(self, login=None, password=None, company_id=None):
        # Можно передать явно, можно взять из settings
        self.login = login or settings.QUICKRESTO_LOGIN
        self.password = password or settings.QUICKRESTO_PASSWORD
        self.company_id = company_id or settings.QUICKRESTO_COMPANY_ID

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
        })

    def _get_auth_header(self) -> str:
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        *,
        params: dict | None = None,
        data: dict | None = None,
    ):
        try:
            response = self.session.request(
                method=method,
                url=f"{self.BASE_URL}{endpoint}",
                params=params,
                json=data,
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            return response.json() if response.content else None

        except requests.RequestException as e:
            raise RuntimeError(f"QuickResto API request failed: {e}") from e

    # ---------- Public API ----------

    def get_products(self):
        return self._make_request(
            "/platform/online/list",
            params={
                "module": "warehouse.nomenclature",
                "companyId": self.company_id,
            },
        )

    def get_orders(self):
        return self._make_request(
            "/platform/online/list",
            params={
                "module": "front.orders",
                "companyId": self.company_id,
            },
        )

    def create_order(self, order_data: dict):
        return self._make_request(
            "/platform/online/create",
            method="POST",
            params={
                "module": "front.orders",
                "companyId": self.company_id,
            },
            data=order_data,
        )
