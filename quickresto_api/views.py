# quickresto_api/views.py - ПОЛНЫЙ ФАЙЛ
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import QuickRestoService


# ==================== VIEWS (для обычных Django views) ====================
class TestAPIView(View):
    """Простой тестовый endpoint для проверки"""

    def get(self, request):
        return JsonResponse({
            'status': 'success',
            'message': 'QuickResto API работает!',
            'data': {
                'test': 'ok',
                'version': '1.0'
            }
        })


# ==================== API VIEWS (для Django REST Framework) ====================
class SearchCustomersView(APIView):
    """Поиск клиентов"""

    def post(self, request):
        query = request.data.get('search', '')
        limit = request.data.get('limit', 50)

        service = QuickRestoService()
        result = service.search_customers(query, limit)

        return Response(result)


class CustomerDetailView(APIView):
    """Детальная информация о клиенте"""

    def get(self, request, customer_guid):
        service = QuickRestoService()
        result = service.get_customer_details(customer_guid)
        return Response(result)

    def put(self, request, customer_guid):
        service = QuickRestoService()
        # Логика обновления клиента
        return Response({"message": "Updated"})


class BusinessListView(APIView):
    """Список организаций"""

    def get(self, request):
        service = QuickRestoService()
        result = service.get_businesses()
        return Response(result)


class MeasureUnitListView(APIView):
    """Список единиц измерения"""

    def get(self, request):
        service = QuickRestoService()
        result = service.get_measure_units()
        return Response(result)