import requests
import time
import hashlib
import hmac


class QuickRestoAPI:
    BASE_URL = "https://api.quickresto.ru"
    TIMEOUT = 30

    def __init__(self, api_key: str, api_secret: str, base_url: str | None = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url or self.BASE_URL

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _generate_signature(self, params: dict) -> str:
        """
        Генерация подписи запроса.
        ВАЖНО: signature НЕ должна входить в саму подпись
        """
        filtered = {k: v for k, v in params.items() if v is not None}

        param_string = "&".join(
            f"{k}={str(v)}" for k, v in sorted(filtered.items())
        )

        return hmac.new(
            self.api_secret.encode(),
            param_string.encode(),
            hashlib.sha256
        ).hexdigest()

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        *,
        params: dict | None = None,
        data: dict | None = None,
    ):
        url = f"{self.base_url}{endpoint}"

        # базовые параметры запроса
        request_params = {
            "key": self.api_key,
            "timestamp": int(time.time()),
        }

        if params:
            request_params.update(params)

        # подпись считается ПОСЛЕ добавления всех params
        request_params["signature"] = self._generate_signature(request_params)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=request_params,
                json=data,
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            return response.json() if response.content else None

        except requests.RequestException as e:
            raise RuntimeError(f"QuickResto API request failed: {e}") from e

    # ---------- Orders ----------

    def get_orders(self, date_from=None, date_to=None, status=None):
        params = {}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        if status:
            params["status"] = status

        return self._make_request("/platform/orders", params=params)

    def get_order_by_id(self, order_id: str):
        return self._make_request(f"/platform/orders/{order_id}")

    def update_order_status(self, order_id: str, status: str):
        return self._make_request(
            f"/platform/orders/{order_id}/status",
            method="PUT",
            data={"status": status},
        )

    # ---------- Menu ----------

    def get_menu_items(self):
        return self._make_request("/platform/menu/items")

    def get_categories(self):
        return self._make_request("/platform/menu/categories")

    # ---------- Tables ----------

    def get_tables(self):
        return self._make_request("/platform/tables")

    def get_table_status(self, table_id: str):
        return self._make_request(f"/platform/tables/{table_id}/status")