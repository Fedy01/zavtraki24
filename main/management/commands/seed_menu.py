from django.core.management.base import BaseCommand
from main.models import MenuItem

class Command(BaseCommand):
    help = "Seed menu items"

    def handle(self, *args, **options):
        items = [
            {"name":"Кофе","description":"Ароматный","price":3.5},
            {"name":"Блинчики","description":"Со сгущёнкой","price":5.0},
            {"name":"Овсянка","description":"С ягодами","price":4.2},
        ]
        for it in items:
            MenuItem.objects.get_or_create(name=it['name'], defaults=it)
        self.stdout.write(self.style.SUCCESS("Seeded menu"))