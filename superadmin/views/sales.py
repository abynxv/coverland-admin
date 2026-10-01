from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from superadmin.models import Sale, SaleItem, Customer, Product
from superadmin.forms import SaleForm, SaleItemFormSet


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10

    def get_queryset(self):
        qs = Sale.objects.select_related('customer').prefetch_related('items__product').order_by('-date', '-id')
        query = self.request.GET.get('q', '').strip()
        customer_id = self.request.GET.get('customer')
        method = self.request.GET.get('payment_method')
        status = self.request.GET.get('payment_status')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        if query:
            qs = qs.filter(
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query) |
                Q(notes__icontains=query)
            )
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if method:
            qs = qs.filter(payment_method=method)
        if status:
            qs = qs.filter(payment_status=status)
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from django.db.models import Sum, F
        from decimal import Decimal
        
        qs = self.get_queryset()
        total_sales = qs.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        outstanding_amount = qs.aggregate(
            outstanding=Sum(F('total_amount') - F('paid_amount'))
        )['outstanding'] or Decimal('0.00')
        
        context['customers'] = Customer.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_customer'] = self.request.GET.get('customer', '')
        context['selected_method'] = self.request.GET.get('payment_method', '')
        context['selected_status'] = self.request.GET.get('payment_status', '')
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['total_sales'] = total_sales
        context['outstanding_amount'] = outstanding_amount
        return context


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'

    def get_queryset(self):
        return Sale.objects.select_related('customer').prefetch_related('items__product')


class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = SaleItemFormSet(self.request.POST)
        else:
            context['items_formset'] = SaleItemFormSet()
        context['products'] = Product.objects.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']

        if items_formset.is_valid():
            forms_with_data = [f for f in items_formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
            if not forms_with_data:
                messages.error(self.request, "Please add at least one item to this sale bill.")
                return self.render_to_response(self.get_context_data(form=form))

            for item_form in forms_with_data:
                product = item_form.cleaned_data.get('product')
                qty = item_form.cleaned_data.get('quantity', 0)
                if product and qty > product.stock_quantity:
                    messages.error(
                        self.request,
                        f"Cannot complete sale: Insufficient stock for '{product.name}'. "
                        f"Available: {product.stock_quantity}, requested: {qty}."
                    )
                    return self.render_to_response(self.get_context_data(form=form))

            with transaction.atomic():
                self.object = form.save(commit=False)
                initial_paid = form.cleaned_data.get('paid_amount', 0)
                if self.object.payment_status == 'Paid':
                    pass # handled by calculate_total
                self.object.save()

                items = items_formset.save(commit=False)
                for item in items:
                    if item.product and item.quantity > 0:
                        item.sale = self.object
                        item.subtotal = item.quantity * item.unit_price
                        item.save()
                        product = item.product
                        product.stock_quantity = max(0, product.stock_quantity - item.quantity)
                        product.save(update_fields=['stock_quantity'])

                self.object.calculate_total()
                
                from superadmin.models import SalePayment
                if self.object.payment_status == 'Paid':
                    initial_paid = self.object.total_amount
                if initial_paid > 0:
                    SalePayment.objects.create(
                        sale=self.object,
                        amount=min(initial_paid, self.object.total_amount),
                        payment_method=self.object.payment_method,
                        date=self.object.date
                    )
                else:
                    self.object.update_payment_status()

                messages.success(
                    self.request,
                    f"Bill {self.object.invoice_number} created successfully. Total: ₹{self.object.total_amount}."
                )
                return redirect('sale_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sale_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        with transaction.atomic():
            # Restore stock
            for item in self.object.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=['stock_quantity'])

            messages.success(
                request,
                f"Sale {self.object.invoice_number} was deleted and item stocks were restored."
            )
            return super().delete(request, *args, **kwargs)


from django.shortcuts import get_object_or_404
from superadmin.models import SalePayment

class SalePaymentCreateView(LoginRequiredMixin, CreateView):
    model = SalePayment
    fields = ['amount', 'payment_method', 'date', 'notes']
    template_name = 'sales/sale_payment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('sale_list')
        
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['amount'].widget.attrs.update({'class': 'form-control', 'step': '0.01', 'min': '0'})
        form.fields['payment_method'].widget.attrs.update({'class': 'form-select'})
        form.fields['date'].widget.attrs.update({'class': 'form-control', 'type': 'date'})
        form.fields['notes'].widget.attrs.update({'class': 'form-control', 'rows': 2})
        return form
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale = get_object_or_404(Sale, pk=self.kwargs['pk'])
        context['sale'] = sale
        context['payments'] = sale.salepayments.all().order_by('-date')
        return context

    def form_valid(self, form):
        sale = get_object_or_404(Sale, pk=self.kwargs['pk'])
        amount = form.cleaned_data['amount']
        
        if amount <= 0:
            form.add_error('amount', 'Payment amount must be greater than 0.')
            return self.form_invalid(form)
            
        if amount > sale.due_amount:
            form.add_error('amount', f'Payment amount (₹{amount}) cannot exceed the outstanding balance (₹{sale.due_amount}).')
            return self.form_invalid(form)
            
        form.instance.sale = sale
        response = super().form_valid(form)
        messages.success(self.request, f"Payment of ₹{amount} recorded for Invoice {sale.invoice_number}.")
        return response

class SaleDetailPublicView(DetailView):
    model = Sale
    template_name = 'sales/sale_detail_public.html'
    context_object_name = 'sale'

    def get_queryset(self):
        return Sale.objects.select_related('customer').prefetch_related('items__product')

