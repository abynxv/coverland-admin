from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Auth
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Products & Stock
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/<int:pk>/adjust/', views.StockAdjustView.as_view(), name='stock_adjust'),

    # Purchases
    path('purchases/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/new/', views.PurchaseCreateView.as_view(), name='purchase_create'),
    path('purchases/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchases/<int:pk>/delete/', views.PurchaseDeleteView.as_view(), name='purchase_delete'),

    # Billing / Sales
    path('sales/', views.SaleListView.as_view(), name='sale_list'),
    path('sales/new/', views.SaleCreateView.as_view(), name='sale_create'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),

    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/new/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),

    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # Expenses
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/new/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
]
