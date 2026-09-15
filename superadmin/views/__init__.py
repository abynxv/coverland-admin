from .auth import CustomLoginView, CustomLogoutView
from .dashboard import DashboardView
from .categories import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)
from .products import (
    ProductListView,
    StockListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    StockAdjustView,
)
from .purchases import (
    PurchaseListView,
    PurchaseDetailView,
    PurchaseCreateView,
    PurchaseDeleteView,
)
from .sales import (
    SaleListView,
    SaleDetailView,
    SaleCreateView,
    SaleDeleteView,
)
from .customers import (
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerDeleteView,
)
from .suppliers import (
    SupplierListView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierDeleteView,
)
from .expenses import (
    ExpenseListView,
    ExpenseCreateView,
    ExpenseUpdateView,
    ExpenseDeleteView,
)

__all__ = [
    'CustomLoginView',
    'CustomLogoutView',
    'DashboardView',
    'CategoryListView',
    'CategoryCreateView',
    'CategoryUpdateView',
    'CategoryDeleteView',
    'ProductListView',
    'StockListView',
    'ProductCreateView',
    'ProductUpdateView',
    'ProductDeleteView',
    'StockAdjustView',
    'PurchaseListView',
    'PurchaseDetailView',
    'PurchaseCreateView',
    'PurchaseDeleteView',
    'SaleListView',
    'SaleDetailView',
    'SaleCreateView',
    'SaleDeleteView',
    'CustomerListView',
    'CustomerCreateView',
    'CustomerUpdateView',
    'CustomerDeleteView',
    'SupplierListView',
    'SupplierCreateView',
    'SupplierUpdateView',
    'SupplierDeleteView',
    'ExpenseListView',
    'ExpenseCreateView',
    'ExpenseUpdateView',
    'ExpenseDeleteView',
]
