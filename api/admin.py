from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.urls import path
from django.template.response import TemplateResponse
from .models import (
    Product,
    Client,
    Quotation,
    QuotationItem,
    PurchaseOrder,
    PurchaseOrderItem,
    Invoice,
    InvoiceItem,
    User
)

from .reports import dashboard_report


# ================= USER =================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff")


# ================= PRODUCTS =================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "unit_price", "category", "type", "date_of_creation")
    search_fields = ("name", "product_id", "category")


# ================= CLIENTS =================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("client_id", "name", "email", "type")
    search_fields = ("name", "client_id")


# ================= QUOTATION ITEMS =================
class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0


# ================= QUOTATIONS =================
@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quotation_id", "client", "date", "total_ht", "total_ttc")
    search_fields = ("quotation_id", "client__name")
    inlines = [QuotationItemInline]


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ("quotation", "product", "quantity", "unit_price")


# ================= PURCHASE ORDER ITEMS =================
class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


# ================= PURCHASE ORDERS =================
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("po_id", "quotation", "client", "status", "date", "total_ht", "total_ttc")
    search_fields = ("po_id", "quotation__quotation_id", "client__name")
    list_filter = ("status", "date")
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ("purchase_order", "product", "quantity", "unit_price")


# ================= INVOICE ITEMS =================
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


# ================= INVOICES =================
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "purchase_order", "client", "date", "total_ht", "total_ttc", "status")
    search_fields = ("invoice_number", "client__name", "purchase_order__po_id")
    list_filter = ("status", "date")
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "product", "quantity", "unit_price")


# ================= REPORTS (NEW) =================
class ReportAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "reports/",
                self.admin_site.admin_view(self.report_view),
                name="reports",
            ),
        ]
        return custom_urls + urls

    def report_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            report=dashboard_report(),
        )
        return TemplateResponse(request, "admin/reports.html", context)
    


class Report(models.Model):
    class Meta:
        verbose_name = "Reports"
        verbose_name_plural = "Reports"


admin.site.register(Report, ReportAdmin)