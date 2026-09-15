import uuid
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    unit = models.CharField(max_length=20, default='pcs', blank=True)

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Purchase(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchases')
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Paid')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def __str__(self):
        return f"Purchase #{self.id} - {self.supplier.name if self.supplier else 'N/A'}"

    class Meta:
        ordering = ['-date', '-id']


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in {self.purchase}"


class Sale(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Credit', 'Credit'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='Cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Paid')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            prefix = timezone.now().strftime('INV-%Y%m%d')
            rand_suffix = uuid.uuid4().hex[:4].upper()
            self.invoice_number = f"{prefix}-{rand_suffix}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def __str__(self):
        return f"Sale {self.invoice_number} ({self.customer.name if self.customer else 'Cash Customer'})"

    class Meta:
        ordering = ['-date', '-id']


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in {self.sale.invoice_number}"


class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('Rent', 'Rent'),
        ('Utilities', 'Utilities (Electricity/Water/Net)'),
        ('Salaries', 'Salaries & Wages'),
        ('Maintenance', 'Maintenance & Repairs'),
        ('Packaging', 'Packaging & Supplies'),
        ('Transport', 'Transport & Shipping'),
        ('Marketing', 'Marketing & Ads'),
        ('General', 'General / Other'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=EXPENSE_CATEGORIES, default='General')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.title} - ${self.amount}"

    class Meta:
        ordering = ['-date', '-id']
