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
    ProductQuickUpdatePriceView,
)
from .purchases import (
    PurchaseListView,
    PurchaseDetailView,
    PurchaseCreateView,
    PurchaseDeleteView,
    PurchaseMarkPaidView,
    PurchasePaymentCreateView,
)
from .sales import (
    SaleListView,
    SaleDetailView,
    SaleCreateView,
    SaleDeleteView,
    SalePaymentCreateView,
    SaleDetailPublicView,
)
from .customers import (
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerDeleteView,
    CustomerDetailView,
)
from .suppliers import (
    SupplierListView,
    SupplierCreateView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierDeleteView,
    SupplierDetailView,
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
    'ProductQuickUpdatePriceView',
    'PurchaseListView',
    'PurchaseDetailView',
    'PurchaseCreateView',
    'PurchaseDeleteView',
    'PurchaseMarkPaidView',
    'PurchasePaymentCreateView',
    'SaleListView',
    'SaleDetailView',
    'SaleCreateView',
    'SaleDeleteView',
    'SalePaymentCreateView',
    'SaleDetailPublicView',
    'CustomerListView',
    'CustomerCreateView',
    'CustomerUpdateView',
    'CustomerDeleteView',
    'CustomerDetailView',
    'SupplierListView',
    'SupplierCreateView',
    'SupplierUpdateView',
    'SupplierDeleteView',
    'SupplierDetailView',
    'ExpenseListView',
    'ExpenseCreateView',
    'ExpenseUpdateView',
    'ExpenseDeleteView',
]
