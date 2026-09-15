from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from decimal import Decimal
from superadmin.models import Expense
from superadmin.forms import ExpenseForm


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 10

    def get_queryset(self):
        qs = Expense.objects.order_by('-date', '-id')
        query = self.request.GET.get('q', '').strip()
        cat = self.request.GET.get('category')

        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if cat:
            qs = qs.filter(category=cat)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['total_expense_amount'] = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        context['categories'] = Expense.EXPENSE_CATEGORIES
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ExpenseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense_list')
    success_message = "Expense '%(title)s' ($%(amount)s) recorded successfully."


class ExpenseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense_list')
    success_message = "Expense '%(title)s' updated successfully."


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Expense '{obj.title}' was deleted successfully.")
        return super().delete(request, *args, **kwargs)
