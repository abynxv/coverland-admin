from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, F
from decimal import Decimal
from superadmin.models import Product, Sale, Purchase, Expense, Customer, Supplier


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aggregated Financials
        total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_purchases = Purchase.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        estimated_margin = total_sales - (total_purchases + total_expenses)

        # Inventory & Catalog Counts
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock_quantity__lte=F('reorder_level')).select_related('category')
        low_stock_count = low_stock_products.count()
        total_customers = Customer.objects.count()
        total_suppliers = Supplier.objects.count()

        # Recent activities
        recent_sales = Sale.objects.select_related('customer').order_by('-date', '-id')[:5]
        recent_purchases = Purchase.objects.select_related('supplier').order_by('-date', '-id')[:5]

        context.update({
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'total_expenses': total_expenses,
            'estimated_margin': estimated_margin,
            'total_products': total_products,
            'low_stock_products': low_stock_products[:6],
            'low_stock_count': low_stock_count,
            'total_customers': total_customers,
            'total_suppliers': total_suppliers,
            'recent_sales': recent_sales,
            'recent_purchases': recent_purchases,
        })
        return context
