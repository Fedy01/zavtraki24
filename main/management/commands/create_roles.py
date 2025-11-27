from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create basic user roles"

    def handle(self, *args, **kwargs):
        roles = ["manager", "courier"]
        for role in roles:
            Group.objects.get_or_create(name=role)

        self.stdout.write(self.style.SUCCESS("Roles created: manager, courier"))