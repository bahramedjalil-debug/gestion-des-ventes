from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product

User = get_user_model()


class ERPAPITest(APITestCase):

    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_user(
            username="admin",
            password="123456",
            is_staff=True
        )

        # Create client user
        self.client_user = User.objects.create_user(
            username="client",
            password="123456",
            is_staff=False
        )

        # Create sample product
        self.product = Product.objects.create(
            name="Laptop",
            unit_price=50000,
            category="Tech",
            type="Device",
            date_of_creation="2026-01-01"
        )

    # ================= LOGIN TEST =================
    def test_login_api(self):
        response = self.client.post("/api/token/", {
            "username": "admin",
            "password": "123456"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    # ================= PRODUCT LIST (CLIENT CAN VIEW) =================
    def test_client_can_view_products(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)

    # ================= PRODUCT CREATE (ONLY ADMIN) =================
    def test_client_cannot_create_product(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post("/api/products/", {
            "name": "Phone",
            "unit_price": 10000,
            "category": "Tech",
            "type": "Device",
            "date_of_creation": "2026-01-01"
        })

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_product(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post("/api/products/", {
            "name": "Phone",
            "unit_price": 10000,
            "category": "Tech",
            "type": "Device",
            "date_of_creation": "2026-01-01"
        })

        self.assertEqual(response.status_code, 200)

    # ================= AUTH TEST =================
    def test_unauthenticated_access_blocked(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 401)