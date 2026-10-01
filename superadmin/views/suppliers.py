from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from superadmin.models import Supplier
from superadmin.forms import SupplierForm


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        qs = Supplier.objects.annotate(
            total_orders=Count('purchases'),
            total_purchased=Sum('purchases__total_amount')
        ).order_by('name')

        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    success_message = "Supplier '%(name)s' was added successfully."


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    success_message = "Supplier '%(name)s' was updated successfully."


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Supplier '{obj.name}' was removed successfully.")
        return super().delete(request, *args, **kwargs)

from django.views.generic import DetailView
from decimal import Decimal

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        purchases = supplier.purchases.all().order_by('-date', '-id')
        
        total_purchased = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_paid = purchases.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')
        total_pending = max(Decimal('0.00'), total_purchased - total_paid)

        context['purchases'] = purchases
        context['total_purchased'] = total_purchased
        context['total_paid'] = total_paid
        context['total_pending'] = total_pending
        return context
