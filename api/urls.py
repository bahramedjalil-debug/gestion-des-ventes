from django.urls import path

from .reports import dashboard_report
from .views import (
    MyTokenObtainPairView,
    RegisterView,
    products,
    product_detail,
    clients,
    client_detail,
    quotations,
    quotation_detail,
    quotation_items,
    purchase_orders,
    convert_to_purchase_order,
    invoices,
    invoice_detail,
    create_invoice_from_po,
)

urlpatterns = [
    # AUTH
    path("token/", MyTokenObtainPairView.as_view(), name="token"),
    path("register/", RegisterView.as_view(), name="register"),
    # path("login/", login, name="login"),

    # PRODUCTS
    path("products/", products),
    path("products/<int:pk>/", product_detail),

    # CLIENTS (READ + UPDATE ONLY, NO CREATE)
    path("clients/", clients),  # GET only now
    path("clients/<int:pk>/", client_detail),

    # QUOTATIONS
    path("quotations/", quotations),
    path("quotations/<int:pk>/", quotation_detail),
    path("quotation-items/", quotation_items),

    # PURCHASE ORDERS
    path("purchase-orders/", purchase_orders),
    path("convert-po/<int:pk>/", convert_to_purchase_order),

    # INVOICES
    path("invoices/", invoices),
    path("invoices/<int:pk>/", invoice_detail),
    path("invoices/from-po/<int:po_id>/", create_invoice_from_po),

    #REPORTS
    path("reports/dashboard/", dashboard_report),
]