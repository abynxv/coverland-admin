from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from superadmin.models import Purchase, PurchaseItem, Supplier, Product
from superadmin.forms import PurchaseForm, PurchaseItemFormSet


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'purchases/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 10

    def get_queryset(self):
        qs = Purchase.objects.select_related('supplier').prefetch_related('items__product').order_by('-date', '-id')
        query = self.request.GET.get('q', '').strip()
        supplier_id = self.request.GET.get('supplier')
        status = self.request.GET.get('payment_status')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        if query:
            qs = qs.filter(
                Q(invoice_number__icontains=query) |
                Q(supplier__name__icontains=query) |
                Q(notes__icontains=query)
            )
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if status:
            qs = qs.filter(payment_status=status)
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from django.db.models import Sum
        from decimal import Decimal
        
        qs = self.get_queryset()
        totals = qs.aggregate(
            total_purchases=Sum('total_amount'),
            total_paid=Sum('paid_amount')
        )
        total_purchases = totals['total_purchases'] or Decimal('0.00')
        total_paid = totals['total_paid'] or Decimal('0.00')
        outstanding_amount = total_purchases - total_paid

        context['suppliers'] = Supplier.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_supplier'] = self.request.GET.get('supplier', '')
        context['selected_status'] = self.request.GET.get('payment_status', '')
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['total_purchases'] = total_purchases
        context['outstanding_amount'] = outstanding_amount
        return context


class PurchaseDetailView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'purchases/purchase_detail.html'
    context_object_name = 'purchase'

    def get_queryset(self):
        return Purchase.objects.select_related('supplier').prefetch_related('items__product')


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchases/purchase_form.html'
    success_url = reverse_lazy('purchase_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = PurchaseItemFormSet(self.request.POST)
        else:
            context['items_formset'] = PurchaseItemFormSet()
        context['products'] = Product.objects.all()
        context['suppliers'] = Supplier.objects.all().order_by('name')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']

        if items_formset.is_valid():
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.save()

                items = items_formset.save(commit=False)
                valid_items_count = 0
                for item in items:
                    if item.product and item.quantity > 0:
                        item.purchase = self.object
                        item.subtotal = item.quantity * item.unit_price
                        item.save()

                        # Update inventory stock
                        product = item.product
                        product.stock_quantity += item.quantity
                        # Optionally update product cost price
                        if item.unit_price > 0:
                            product.cost_price = item.unit_price
                        product.save(update_fields=['stock_quantity', 'cost_price'])
                        valid_items_count += 1

                # Recompute total amount
                self.object.calculate_total()
                
                initial_paid = form.cleaned_data.get('paid_amount', 0)
                from superadmin.models import PurchasePayment
                if self.object.payment_status == 'Paid':
                    initial_paid = self.object.total_amount
                if initial_paid > 0:
                    PurchasePayment.objects.create(
                        purchase=self.object,
                        amount=min(initial_paid, self.object.total_amount),
                        payment_method='Cash', # default
                        date=self.object.date
                    )
                else:
                    self.object.update_payment_status()

                messages.success(
                    self.request,
                    f"Purchase #{self.object.id} ({self.object.invoice_number or 'Direct'}) recorded successfully. "
                    f"Stock updated for {valid_items_count} item(s)."
                )
                return redirect('purchase_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class PurchaseDeleteView(LoginRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'purchases/purchase_confirm_delete.html'
    success_url = reverse_lazy('purchase_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        with transaction.atomic():
            # Rollback inventory
            for item in self.object.items.all():
                item.product.stock_quantity = max(0, item.product.stock_quantity - item.quantity)
                item.product.save(update_fields=['stock_quantity'])

            messages.success(
                request,
                f"Purchase #{self.object.id} was deleted and product inventory was rolled back."
            )
            return super().delete(request, *args, **kwargs)

from django.views import View
from django.shortcuts import get_object_or_404
from superadmin.models import PurchasePayment

class PurchaseMarkPaidView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        purchase = get_object_or_404(Purchase, pk=pk)
        if purchase.payment_status != 'Paid' and purchase.due_amount > 0:
            PurchasePayment.objects.create(
                purchase=purchase,
                amount=purchase.due_amount,
                payment_method='Cash',
                date=timezone.now().date()
            )
            messages.success(request, f"Purchase #{purchase.id} marked as fully paid.")
        
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        if next_url:
            return redirect(next_url)
        return redirect('purchase_list')

class PurchasePaymentCreateView(LoginRequiredMixin, CreateView):
    model = PurchasePayment
    fields = ['amount', 'payment_method', 'date', 'notes']
    template_name = 'purchases/purchase_payment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('purchase_list')
        
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['amount'].widget.attrs.update({'class': 'form-control', 'step': '0.01', 'min': '0'})
        form.fields['payment_method'].widget.attrs.update({'class': 'form-select'})
        form.fields['date'].widget.attrs.update({'class': 'form-control', 'type': 'date'})
        form.fields['notes'].widget.attrs.update({'class': 'form-control', 'rows': 2})
        return form
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchase = get_object_or_404(Purchase, pk=self.kwargs['pk'])
        context['purchase'] = purchase
        context['payments'] = purchase.purchasepayments.all().order_by('-date')
        return context

    def form_valid(self, form):
        purchase = get_object_or_404(Purchase, pk=self.kwargs['pk'])
        amount = form.cleaned_data['amount']
        
        if amount <= 0:
            form.add_error('amount', 'Payment amount must be greater than 0.')
            return self.form_invalid(form)
            
        if amount > purchase.due_amount:
            form.add_error('amount', f'Payment amount (₹{amount}) cannot exceed the outstanding balance (₹{purchase.due_amount}).')
            return self.form_invalid(form)
            
        form.instance.purchase = purchase
        response = super().form_valid(form)
        messages.success(self.request, f"Payment of ₹{amount} recorded for Purchase #{purchase.id}.")
        return response
