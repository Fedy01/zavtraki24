from django.db import models

class Table(models.Model):
    name = models.CharField(max_length=100)
    seats_count = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.name} ({self.seats_count})"