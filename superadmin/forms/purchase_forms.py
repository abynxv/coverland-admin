from django import forms
from django.forms import inlineformset_factory
from superadmin.models import Purchase, PurchaseItem, Product


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'invoice_number', 'date', 'payment_status', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SUP-INV-9901'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional purchase details, shipping notes...'}),
        }


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select item-product'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control item-qty', 'min': '1', 'value': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control item-price', 'step': '0.01', 'min': '0'}),
        }


PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True
)
