from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
import uuid


# ===================== AUTO ID GENERATORS =====================

def generate_client_id():
    return f"CL-{uuid.uuid4().hex[:8].upper()}"

def generate_product_id():
    return f"PR-{uuid.uuid4().hex[:8].upper()}"

def generate_quotation_id():
    return f"QUO-{uuid.uuid4().hex[:10].upper()}"

def generate_po_id():
    return f"PO-{uuid.uuid4().hex[:10].upper()}"

def generate_invoice_number():
    return f"INV-{uuid.uuid4().hex[:10].upper()}"


# ===================== USER =====================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return self.username


# ===================== CLIENT =====================
class Client(models.Model):
    client_id = models.CharField(max_length=20, unique=True, blank=True, default=generate_client_id)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    type = models.CharField(max_length=50)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = generate_client_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ===================== PRODUCT =====================
class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True, blank=True, default=generate_product_id)
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    date_of_creation = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("in_stock", "In Stock"),
            ("out_of_stock", "Out of Stock"),
        ],
        default="in_stock"
    )

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = generate_product_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ===================== QUOTATION =====================
class Quotation(models.Model):
    quotation_id = models.CharField(max_length=50, unique=True, blank=True, default=generate_quotation_id)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=20, default="Draft")

    def save(self, *args, **kwargs):
        if not self.quotation_id:
            self.quotation_id = generate_quotation_id()
        super().save(*args, **kwargs)


# ===================== QUOTATION ITEM =====================
class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


# ===================== PURCHASE ORDER =====================
class PurchaseOrder(models.Model):
    po_id = models.CharField(max_length=50, unique=True, blank=True, default=generate_po_id)
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    date = models.DateField(auto_now_add=True)

    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, default="Draft")

    def save(self, *args, **kwargs):
        if not self.po_id:
            self.po_id = generate_po_id()
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


# ===================== INVOICE =====================
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, default=generate_invoice_number)

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    date = models.DateField(auto_now_add=True)

    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, default="unpaid")

    payment_method = models.CharField(
        max_length=10,
        choices=[("cash", "Cash"), ("card", "Card")],
        default="cash"
    )

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = generate_invoice_number()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)