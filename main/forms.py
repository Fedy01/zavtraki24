from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "phone", "address", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
