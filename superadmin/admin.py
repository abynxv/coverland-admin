from django.contrib import admin
from .models import Category, Product, Customer, Supplier, Purchase, Sale, Expense

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Supplier)
admin.site.register(Purchase)
admin.site.register(Sale)
admin.site.register(Expense)
