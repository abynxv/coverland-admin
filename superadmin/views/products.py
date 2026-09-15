from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect
from superadmin.models import Product, Category
from superadmin.forms import ProductForm, StockAdjustmentForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        qs = Product.objects.select_related('category').order_by('name')
        query = self.request.GET.get('q', '').strip()
        category_id = self.request.GET.get('category')
        stock_filter = self.request.GET.get('stock_status')

        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
        if category_id:
            qs = qs.filter(category_id=category_id)
        if stock_filter == 'low':
            qs = qs.filter(stock_quantity__lte=F('reorder_level'), stock_quantity__gt=0)
        elif stock_filter == 'out':
            qs = qs.filter(stock_quantity__lte=0)
        elif stock_filter == 'in_stock':
            qs = qs.filter(stock_quantity__gt=F('reorder_level'))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_stock_status'] = self.request.GET.get('stock_status', '')
        context['is_stock_view'] = False
        return context


class StockListView(ProductListView):
    template_name = 'products/stock_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_stock_view'] = True
        context['total_products'] = Product.objects.count()
        context['low_stock_count'] = Product.objects.filter(stock_quantity__lte=F('reorder_level'), stock_quantity__gt=0).count()
        context['out_of_stock_count'] = Product.objects.filter(stock_quantity__lte=0).count()
        return context


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')
    success_message = "Product '%(name)s' was created successfully."


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')
    success_message = "Product '%(name)s' was updated successfully."


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Product '{obj.name}' was deleted successfully.")
        return super().delete(request, *args, **kwargs)


class StockAdjustView(LoginRequiredMixin, FormView):
    form_class = StockAdjustmentForm
    template_name = 'products/stock_adjust.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def form_valid(self, form):
        adj_type = form.cleaned_data['adjustment_type']
        qty = form.cleaned_data['quantity']

        if adj_type == 'add':
            self.product.stock_quantity += qty
            action_desc = f"added {qty} units to"
        else:
            self.product.stock_quantity = qty
            action_desc = f"set stock to {qty} units for"

        self.product.save(update_fields=['stock_quantity'])
        messages.success(self.request, f"Successfully {action_desc} {self.product.name}. Current stock: {self.product.stock_quantity}.")
        return redirect('stock_list')
