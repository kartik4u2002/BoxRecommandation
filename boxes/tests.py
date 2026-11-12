from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Box


class BoxModelTestCase(TestCase):
    """
    Unit tests for Box model creation, validation and constraints.
    """

    def setUp(self):
        self.valid_data = {
            'name': 'Medium Shipper',
            'length': Decimal('40.00'),
            'width': Decimal('30.00'),
            'height': Decimal('20.00'),
            'max_weight': Decimal('15.00'),
            'cost': Decimal('25.50'),
            'is_active': True,
        }

    def test_box_creation(self):
        box = Box.objects.create(**self.valid_data)
        self.assertIsNotNone(box.id)
        self.assertEqual(box.name, 'Medium Shipper')
        self.assertEqual(box.length, Decimal('40.00'))
        self.assertEqual(box.width, Decimal('30.00'))
        self.assertEqual(box.height, Decimal('20.00'))
        self.assertEqual(box.max_weight, Decimal('15.00'))
        self.assertEqual(box.cost, Decimal('25.50'))
        self.assertTrue(box.is_active)

    def test_box_retrieval(self):
        created = Box.objects.create(**self.valid_data)
        retrieved = Box.objects.get(id=created.id)
        self.assertEqual(retrieved.name, created.name)
        expected_volume = Decimal('40.00') * Decimal('30.00') * Decimal('20.00')
        self.assertEqual(retrieved.volume, expected_volume)

    def test_negative_cost_rejection(self):
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Negative Cost Box',
                length=Decimal('20.00'),
                width=Decimal('20.00'),
                height=Decimal('20.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('-5.00')
            )

    def test_invalid_dimensions_rejection(self):
        # Negative length
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Neg Length',
                length=Decimal('-1.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('5.00')
            )

        # Zero length
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Zero Length',
                length=Decimal('0.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('5.00')
            )

        # Negative width
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Neg Width',
                length=Decimal('10.00'),
                width=Decimal('-1.00'),
                height=Decimal('10.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('5.00')
            )

        # Zero width
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Zero Width',
                length=Decimal('10.00'),
                width=Decimal('0.00'),
                height=Decimal('10.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('5.00')
            )

        # Negative height
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Neg Height',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('-1.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('5.00')
            )

        # Zero height
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Zero Height',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('0.00'),
                max_weight=Decimal('10.00'),
                cost=Decimal('5.00')
            )

    def test_invalid_maximum_weight_rejection(self):
        # Negative max weight
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Neg Weight Box',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                max_weight=Decimal('-10.00'),
                cost=Decimal('5.00')
            )

        # Zero max weight
        with self.assertRaises(ValidationError):
            Box.objects.create(
                name='Zero Weight Box',
                length=Decimal('10.00'),
                width=Decimal('10.00'),
                height=Decimal('10.00'),
                max_weight=Decimal('0.00'),
                cost=Decimal('5.00')
            )

    def test_inactive_box_exclusion(self):
        active_box = Box.objects.create(**self.valid_data)
        inactive_data = self.valid_data.copy()
        inactive_data['name'] = 'Retired Box'
        inactive_data['is_active'] = False
        inactive_box = Box.objects.create(**inactive_data)

        active_boxes = Box.objects.filter(is_active=True)
        self.assertIn(active_box, active_boxes)
        self.assertNotIn(inactive_box, active_boxes)


class BoxAPITestCase(APITestCase):
    """
    Integration tests for Box REST API endpoints.
    """

    def test_create_box_success(self):
        url = '/api/boxes/'
        payload = {
            'name': 'Large Box',
            'length': '60.00',
            'width': '40.00',
            'height': '30.00',
            'max_weight': '25.00',
            'cost': '45.00',
            'is_active': True,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Large Box')
        self.assertEqual(Decimal(str(response.data['cost'])), Decimal('45.00'))

    def test_list_boxes(self):
        Box.objects.create(
            name='Box 1', length=Decimal('10'), width=Decimal('10'),
            height=Decimal('10'), max_weight=Decimal('5'), cost=Decimal('10'),
            is_active=True
        )
        Box.objects.create(
            name='Box 2', length=Decimal('20'), width=Decimal('20'),
            height=Decimal('20'), max_weight=Decimal('10'), cost=Decimal('20'),
            is_active=False
        )
        url = '/api/boxes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_box_api_negative_cost_validation(self):
        url = '/api/boxes/'
        payload = {
            'name': 'Negative Cost',
            'length': '20.00',
            'width': '20.00',
            'height': '20.00',
            'max_weight': '10.00',
            'cost': '-1.00',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cost', response.data)

    def test_box_api_invalid_dimensions_validation(self):
        url = '/api/boxes/'
        payload = {
            'name': 'Zero Length',
            'length': '0.00',
            'width': '20.00',
            'height': '20.00',
            'max_weight': '10.00',
            'cost': '5.00',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('length', response.data)

    def test_box_api_invalid_max_weight_validation(self):
        url = '/api/boxes/'
        payload = {
            'name': 'Zero Max Weight',
            'length': '20.00',
            'width': '20.00',
            'height': '20.00',
            'max_weight': '0.00',
            'cost': '5.00',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max_weight', response.data)
