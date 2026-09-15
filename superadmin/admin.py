from django.contrib import admin
from .models import Category, Product, Customer, Supplier, Purchase, PurchaseItem, Sale, SaleItem, Expense


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'invoice_number', 'date', 'total_amount', 'payment_status')
    list_filter = ('payment_status', 'date')
    search_fields = ('invoice_number', 'supplier__name')
    inlines = [PurchaseItemInline]


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'date', 'total_amount', 'payment_method', 'payment_status')
    list_filter = ('payment_method', 'payment_status', 'date')
    search_fields = ('invoice_number', 'customer__name')
    inlines = [SaleItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stock_quantity', 'reorder_level', 'cost_price', 'selling_price')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'date')
    list_filter = ('category', 'date')
    search_fields = ('title', 'description')
