from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .models import PurchaseOrderItem
from .serializers import *


# ===================== AUTH =====================

class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username
        token["is_staff"] = user.is_staff
        token["role"] = "admin" if user.is_staff else "client"

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Client.objects.create(
        user=user,
        name=user.username,
        type="regular"  
    )

        return Response({"message": "User created"})


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(
        username=request.data["username"],
        password=request.data["password"]
    )

    if user:
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": "admin" if user.is_staff else "client",
            "user": user.username
        })

    return Response({"error": "Invalid credentials"}, status=401)


# ===================== PRODUCTS =====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products(request):

    # ALL authenticated users can view products
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # only admin can modify
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({"error": "Forbidden"}, status=403)

        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):

    try:
        obj = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if request.method in ['PUT', 'DELETE'] and not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)

    if request.method == 'GET':
        return Response(ProductSerializer(obj).data)

    if request.method == 'PUT':
        serializer = ProductSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    obj.delete()
    return Response({"message": "Deleted"})


# ===================== CLIENTS (READ ONLY) =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clients(request):

    # Always exclude admins from client list
    clients_qs = Client.objects.filter(user__is_staff=False)

    # If you want clients to only see themselves
    if not request.user.is_staff:
        clients_qs = clients_qs.filter(user=request.user)

    return Response(ClientSerializer(clients_qs, many=True).data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def client_detail(request, pk):

    try:
        obj = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if not request.user.is_staff and obj.user != request.user:
        return Response({"error": "Forbidden"}, status=403)

    if request.method == 'GET':
        return Response(ClientSerializer(obj).data)

    if request.method == 'PUT':
        serializer = ClientSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    obj.delete()
    return Response({"message": "Deleted"})


# ===================== QUOTATIONS =====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quotations(request):

    if request.method == 'POST' and not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)

    if request.method == 'POST':
        serializer = QuotationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    qs = Quotation.objects.all() if request.user.is_staff else Quotation.objects.filter(client__user=request.user)
    return Response(QuotationSerializer(qs, many=True).data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def quotation_detail(request, pk):

    try:
        obj = Quotation.objects.get(pk=pk)
    except Quotation.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if not request.user.is_staff and obj.client.user != request.user:
        return Response({"error": "Forbidden"}, status=403)

    if request.method == 'GET':
        return Response(QuotationSerializer(obj).data)

    if request.method == 'PUT':
        serializer = QuotationSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    obj.delete()
    return Response({"message": "Deleted"})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quotation_items(request):

    if request.method == 'GET':
        items = QuotationItem.objects.all()
        return Response(QuotationItemSerializer(items, many=True).data)

    if not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)

    serializer = QuotationItemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ===================== PURCHASE ORDERS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_orders(request):

    qs = PurchaseOrder.objects.all() if request.user.is_staff else PurchaseOrder.objects.filter(client__user=request.user)
    return Response(PurchaseOrderSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_to_purchase_order(request, pk):

    if not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)

    try:
        quotation = Quotation.objects.get(pk=pk)
    except Quotation.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    
    if hasattr(quotation, 'purchaseorder'):
        return Response({"error": "Already converted"}, status=400)

    po = PurchaseOrder.objects.create(
        po_id=f"PO-{quotation.id}-{PurchaseOrder.objects.count()+1}",
        quotation=quotation,
        client=quotation.client,
        total_ht=quotation.total_ht or 0,
        total_ttc=quotation.total_ttc or 0
    )

    for item in quotation.items.all():
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.unit_price
        )

    quotation.status = "Accepted"
    quotation.save()

    return Response({
        "message": "Converted",
        "po_id": po.po_id
    })


# ===================== INVOICES =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoices(request):

    qs = Invoice.objects.all() if request.user.is_staff else Invoice.objects.filter(client__user=request.user)
    return Response(InvoiceSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_detail(request, pk):

    try:
        obj = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if not request.user.is_staff and obj.client.user != request.user:
        return Response({"error": "Forbidden"}, status=403)

    return Response(InvoiceSerializer(obj).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice_from_po(request, po_id):

    if not request.user.is_staff:
        return Response({"error": "Forbidden"}, status=403)

    try:
        po = PurchaseOrder.objects.get(id=po_id)
    except PurchaseOrder.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    invoice = Invoice.objects.create(
        invoice_number=f"INV-{po.id}",
        purchase_order=po,
        client=po.client,
        total_ht=po.total_ht,
        total_ttc=po.total_ttc
    )

    for item in po.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.unit_price
        )

    return Response({
        "message": "Invoice created",
        "invoice_id": invoice.id
    })