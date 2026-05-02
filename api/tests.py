from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Product, Client

User = get_user_model()


class ProductTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="123456",
            is_staff=True
        )

    def test_create_product(self):
        product = Product.objects.create(
            name="Test Product",
            unit_price=1000,
            category="Tech",
            type="Device",
            date_of_creation="2026-01-01"
        )

        self.assertEqual(product.name, "Test Product")


class ClientTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="client1",
            password="123456"
        )

    def test_client_creation(self):
        client = Client.objects.create(
            user=self.user,
            name="Client 1",
            type="regular"
        )

        self.assertEqual(client.user.username, "client1")