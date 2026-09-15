from django import forms
from django.forms import inlineformset_factory
from superadmin.models import Sale, SaleItem, Product


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'payment_status', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional bill memo or customer note...'}),
        }


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select item-product'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control item-qty', 'min': '1', 'value': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control item-price', 'step': '0.01', 'min': '0'}),
        }


SaleItemFormSet = inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True
)
