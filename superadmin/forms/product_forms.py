from django import forms
from superadmin.models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'cost_price', 'selling_price', 'stock_quantity', 'reorder_level', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Matte Black Silicon Case iPhone 15'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'pcs, pack, box'}),
        }


class StockAdjustmentForm(forms.Form):
    adjustment_type = forms.ChoiceField(
        choices=[('add', 'Add Stock (+)'), ('set', 'Set Exact Count (=)')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for adjustment (e.g. physical count audit)'})
    )
