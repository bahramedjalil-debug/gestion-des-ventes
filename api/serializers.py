from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = self.user.username
        data["role"] = "admin" if self.user.is_staff else "client"

        return data
# ================= AUTH =================
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role='client'
        )


# ================= PRODUCT =================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


# ================= CLIENT =================
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True}
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request context missing")

        return Client.objects.create(
            user=request.user,
            **validated_data
        )


# ================= QUOTATION =================
class QuotationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = QuotationItem
        fields = "__all__"


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    client_name = serializers.ReadOnlyField(source="client.name")

    class Meta:
        model = Quotation
        fields = "__all__"


# ================= PO =================
class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = PurchaseOrderItem
        fields = "__all__"


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    client_name = serializers.ReadOnlyField(source="client.name")

    class Meta:
        model = PurchaseOrder
        fields = "__all__"


# ================= INVOICE =================
class InvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    client_name = serializers.ReadOnlyField(source="client.name")

    class Meta:
        model = Invoice
        fields = "__all__"