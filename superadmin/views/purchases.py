from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
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

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_supplier'] = self.request.GET.get('supplier', '')
        context['selected_status'] = self.request.GET.get('payment_status', '')
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
