from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product


class ProductModelTestCase(TestCase):
    """
    Unit tests for Product model validation and behavior.
    """

    def setUp(self):
        self.valid_data = {
            'name': 'Wireless Mouse',
            'length': Decimal('12.50'),
            'width': Decimal('6.50'),
            'height': Decimal('4.00'),
            'weight': Decimal('0.15'),
        }

    def test_product_creation(self):
        product = Product.objects.create(**self.valid_data)
        self.assertIsNotNone(product.id)
        self.assertEqual(product.name, 'Wireless Mouse')
        self.assertEqual(product.length, Decimal('12.50'))
        self.assertEqual(product.width, Decimal('6.50'))
        self.assertEqual(product.height, Decimal('4.00'))
        self.assertEqual(product.weight, Decimal('0.15'))

    def test_product_retrieval(self):
        created = Product.objects.create(**self.valid_data)
        retrieved = Product.objects.get(id=created.id)
        self.assertEqual(retrieved.name, created.name)
        self.assertEqual(retrieved.volume, Decimal('12.50') * Decimal('6.50') * Decimal('4.00'))

    def test_negative_dimensions_rejection(self):
        # Length negative
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Invalid Length',
                length=Decimal('-5.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                weight=Decimal('1.00')
            )

        # Width negative
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Invalid Width',
                length=Decimal('10.00'),
                width=Decimal('-5.00'),
                height=Decimal('10.00'),
                weight=Decimal('1.00')
            )

        # Height negative
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Invalid Height',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('-5.00'),
                weight=Decimal('1.00')
            )

    def test_zero_dimensions_rejection(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Zero Length',
                length=Decimal('0.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                weight=Decimal('1.00')
            )

        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Zero Width',
                length=Decimal('10.00'),
                width=Decimal('0.00'),
                height=Decimal('10.00'),
                weight=Decimal('1.00')
            )

        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Zero Height',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('0.00'),
                weight=Decimal('1.00')
            )

    def test_negative_weight_rejection(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name='Negative Weight',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                weight=Decimal('-0.50')
            )


class ProductAPITestCase(APITestCase):
    """
    Integration tests for Product REST API endpoints.
    """

    def test_create_product_success(self):
        url = '/api/products/'
        payload = {
            'name': 'Keyboard',
            'length': '45.00',
            'width': '15.00',
            'height': '3.50',
            'weight': '0.80'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Keyboard')
        self.assertEqual(Decimal(str(response.data['length'])), Decimal('45.00'))

    def test_list_products(self):
        Product.objects.create(
            name='Item A', length=Decimal('10'), width=Decimal('10'),
            height=Decimal('10'), weight=Decimal('1')
        )
        Product.objects.create(
            name='Item B', length=Decimal('20'), width=Decimal('20'),
            height=Decimal('20'), weight=Decimal('2')
        )
        url = '/api/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_product_api_negative_dimensions_validation(self):
        url = '/api/products/'
        payload = {
            'name': 'Bad Product',
            'length': '-10.00',
            'width': '5.00',
            'height': '5.00',
            'weight': '1.00'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('length', response.data)

    def test_product_api_zero_dimensions_validation(self):
        url = '/api/products/'
        payload = {
            'name': 'Bad Product Zero',
            'length': '0.00',
            'width': '5.00',
            'height': '5.00',
            'weight': '1.00'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('length', response.data)

    def test_product_api_negative_weight_validation(self):
        url = '/api/products/'
        payload = {
            'name': 'Bad Weight Product',
            'length': '10.00',
            'width': '5.00',
            'height': '5.00',
            'weight': '-2.00'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', response.data)
