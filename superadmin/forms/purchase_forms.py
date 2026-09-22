from django import forms
from django.forms import inlineformset_factory
from superadmin.models import Purchase, PurchaseItem, Product


class PurchaseForm(forms.ModelForm):
    paid_amount = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'})
    )

    class Meta:
        model = Purchase
        fields = ['supplier', 'invoice_number', 'date', 'payment_status', 'paid_amount', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SUP-INV-9901'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional purchase details, shipping notes...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_status = cleaned_data.get('payment_status')
        paid_amount = cleaned_data.get('paid_amount')

        if payment_status == 'Partial':
            if paid_amount is None or paid_amount <= 0:
                self.add_error('paid_amount', 'Please enter a valid amount greater than 0 for partial payment.')
        else:
            if paid_amount is None:
                cleaned_data['paid_amount'] = 0

        return cleaned_data


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
