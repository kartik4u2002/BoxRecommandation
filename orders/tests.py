from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product
from .models import Order, OrderItem


class OrderModelTestCase(TestCase):
    """
    Unit tests for Order and OrderItem models.
    """

    def setUp(self):
        self.product1 = Product.objects.create(
            name='Product 1',
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            weight=Decimal('2.00')
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            length=Decimal('20.00'),
            width=Decimal('10.00'),
            height=Decimal('5.00'),
            weight=Decimal('1.50')
        )

    def test_order_creation_and_retrieval(self):
        order = Order.objects.create(customer_name='John Doe')
        self.assertIsNotNone(order.id)
        self.assertEqual(order.customer_name, 'John Doe')
        self.assertEqual(order.status, 'PENDING')
        self.assertIsNotNone(order.created_at)

        retrieved = Order.objects.get(id=order.id)
        self.assertEqual(retrieved.customer_name, 'John Doe')

    def test_adding_multiple_products_and_quantities(self):
        order = Order.objects.create(customer_name='Alice Smith')
        item1 = OrderItem.objects.create(order=order, product=self.product1, quantity=2)
        item2 = OrderItem.objects.create(order=order, product=self.product2, quantity=3)

        self.assertEqual(order.items.count(), 2)

        # Expected total weight: (2 * 2.00) + (3 * 1.50) = 4.00 + 4.50 = 8.50
        self.assertEqual(order.total_weight, Decimal('8.50'))

        # Expected total volume: (2 * 1000) + (3 * 1000) = 5000
        self.assertEqual(order.total_volume, Decimal('5000.00'))

    def test_zero_quantity_rejection(self):
        order = Order.objects.create(customer_name='Bob')
        with self.assertRaises(ValidationError):
            OrderItem.objects.create(order=order, product=self.product1, quantity=0)

    def test_negative_quantity_rejection(self):
        order = Order.objects.create(customer_name='Bob')
        with self.assertRaises(ValidationError):
            OrderItem.objects.create(order=order, product=self.product1, quantity=-1)


class OrderAPITestCase(APITestCase):
    """
    Integration tests for Order REST API endpoints.
    """

    def setUp(self):
        self.product1 = Product.objects.create(
            name='Coffee Mug',
            length=Decimal('12.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            weight=Decimal('0.40')
        )
        self.product2 = Product.objects.create(
            name='Notebook',
            length=Decimal('25.00'),
            width=Decimal('18.00'),
            height=Decimal('2.00'),
            weight=Decimal('0.30')
        )

    def test_create_order_api_success(self):
        url = '/api/orders/'
        payload = {
            'customer_name': 'Jane Doe',
            'items': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1},
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_name'], 'Jane Doe')
        self.assertEqual(len(response.data['items']), 2)

    def test_retrieve_order_api(self):
        order = Order.objects.create(customer_name='Clark Kent')
        OrderItem.objects.create(order=order, product=self.product1, quantity=3)

        url = f'/api/orders/{order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer_name'], 'Clark Kent')
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 3)

    def test_empty_order_api_rejection(self):
        url = '/api/orders/'
        payload = {
            'customer_name': 'Empty Order Customer',
            'items': []
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_zero_or_negative_quantity_api_rejection(self):
        url = '/api/orders/'
        payload = {
            'customer_name': 'Invalid Quantity Customer',
            'items': [
                {'product_id': self.product1.id, 'quantity': 0}
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        payload_neg = {
            'customer_name': 'Invalid Quantity Customer',
            'items': [
                {'product_id': self.product1.id, 'quantity': -2}
            ]
        }
        response_neg = self.client.post(url, payload_neg, format='json')
        self.assertEqual(response_neg.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_product_api_rejection(self):
        url = '/api/orders/'
        payload = {
            'customer_name': 'Bad Product Order',
            'items': [
                {'product_id': 99999, 'quantity': 1}
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
