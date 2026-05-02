from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Client, Product, Quotation, QuotationItem, PurchaseOrder

User = get_user_model()


class ERPFlowTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="123456",
            is_staff=True
        )

        self.user = User.objects.create_user(
            username="client",
            password="123456",
            is_staff=False
        )

        self.client_obj = Client.objects.create(
            user=self.user,
            name="Client Test",
            type="regular"
        )

        self.product = Product.objects.create(
            name="Laptop",
            unit_price=1000,
            category="Tech",
            type="Device",
            date_of_creation="2026-01-01"
        )

        self.quotation = Quotation.objects.create(
            client=self.client_obj,
            total_ht=1000,
            total_ttc=1200
        )

        QuotationItem.objects.create(
            quotation=self.quotation,
            product=self.product,
            quantity=1,
            unit_price=1000
        )

    # ================= FLOW 1 =================
    def test_quotation_exists(self):
        self.assertEqual(self.quotation.client.name, "Client Test")

    # ================= FLOW 2 =================
    def test_convert_to_purchase_order(self):
        po = PurchaseOrder.objects.create(
            quotation=self.quotation,
            client=self.client_obj,
            total_ht=1000,
            total_ttc=1200
        )

        self.assertEqual(po.client.name, "Client Test")
        self.assertEqual(po.total_ht, 1000)