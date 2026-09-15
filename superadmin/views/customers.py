from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from superadmin.models import Customer
from superadmin.forms import CustomerForm


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_queryset(self):
        qs = Customer.objects.annotate(
            total_purchases_count=Count('sales'),
            total_spent=Sum('sales__total_amount')
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


class CustomerCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')
    success_message = "Customer '%(name)s' was added successfully."


class CustomerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')
    success_message = "Customer '%(name)s' was updated successfully."


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Customer '{obj.name}' was removed successfully.")
        return super().delete(request, *args, **kwargs)
