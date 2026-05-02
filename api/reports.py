from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product, Client, Invoice

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_report(request):

    total_products = Product.objects.count()
    in_stock = Product.objects.filter(status="in_stock").count()
    out_stock = Product.objects.filter(status="out_of_stock").count()

    total_clients = Client.objects.count()
    total_invoices = Invoice.objects.count()

    total_revenue = sum(i.total_ttc for i in Invoice.objects.all())

    return Response({
        "products": {
            "total": total_products,
            "in_stock": in_stock,
            "out_of_stock": out_stock
        },
        "clients": total_clients,
        "invoices": total_invoices,
        "revenue": float(total_revenue)
    })