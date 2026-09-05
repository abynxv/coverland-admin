from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import F
from .models import Product

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch low stock products (reorder_level >= stock_quantity)
        context['low_stock_products'] = Product.objects.filter(stock_quantity__lte=F('reorder_level'))
        return context
