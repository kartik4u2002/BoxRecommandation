from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product
from boxes.models import Box
from orders.models import Order, OrderItem
from .services.packing_engine import PackingEngine, ItemToPack
from .services.box_selector import BoxSelector


class PackingEngineTestCase(TestCase):
    """
    Unit tests for 3D packing engine heuristics, rotation, collision,
    and boundary constraints.
    """

    def test_single_product_fits(self):
        item = ItemToPack('Cube', Decimal('5'), Decimal('5'), Decimal('5'))
        success, placed = PackingEngine.pack(
            box_length=Decimal('10'),
            box_width=Decimal('10'),
            box_height=Decimal('10'),
            items=[item]
        )
        self.assertTrue(success)
        self.assertEqual(len(placed), 1)
        self.assertEqual(placed[0].x, Decimal('0'))
        self.assertEqual(placed[0].y, Decimal('0'))
        self.assertEqual(placed[0].z, Decimal('0'))

    def test_product_does_not_fit(self):
        item = ItemToPack('Too Big', Decimal('15'), Decimal('5'), Decimal('5'))
        success, placed = PackingEngine.pack(
            box_length=Decimal('10'),
            box_width=Decimal('10'),
            box_height=Decimal('10'),
            items=[item]
        )
        self.assertFalse(success)
        self.assertEqual(len(placed), 0)

    def test_product_fits_after_rotation(self):
        # Item length 15 cannot fit box length 10 without rotation,
        # but fits along box width 20 when rotated.
        item = ItemToPack('Long Item', Decimal('15'), Decimal('5'), Decimal('5'))
        success, placed = PackingEngine.pack(
            box_length=Decimal('10'),
            box_width=Decimal('20'),
            box_height=Decimal('10'),
            items=[item]
        )
        self.assertTrue(success)
        self.assertEqual(len(placed), 1)
        # Verify the placed item dimensions fit within (10, 20, 10)
        p = placed[0]
        self.assertLessEqual(p.x + p.dx, Decimal('10'))
        self.assertLessEqual(p.y + p.dy, Decimal('20'))
        self.assertLessEqual(p.z + p.dz, Decimal('10'))

    def test_multiple_products_fit(self):
        items = [
            ItemToPack('Box A', Decimal('5'), Decimal('10'), Decimal('5')),
            ItemToPack('Box B', Decimal('5'), Decimal('10'), Decimal('5')),
        ]
        success, placed = PackingEngine.pack(
            box_length=Decimal('10'),
            box_width=Decimal('10'),
            box_height=Decimal('5'),
            items=items
        )
        self.assertTrue(success)
        self.assertEqual(len(placed), 2)

    def test_products_individually_fit_but_cannot_be_packed_together(self):
        # Two 6x6x6 cubes in a 10x10x10 box.
        # Combined volume = 216 * 2 = 432 <= 1000 (volume check alone would pass!).
        # But along any single dimension, 6 + 6 = 12 > 10. They cannot pack together.
        items = [
            ItemToPack('Cube 1', Decimal('6'), Decimal('6'), Decimal('6')),
            ItemToPack('Cube 2', Decimal('6'), Decimal('6'), Decimal('6')),
        ]
        success, placed = PackingEngine.pack(
            box_length=Decimal('10'),
            box_width=Decimal('10'),
            box_height=Decimal('10'),
            items=items
        )
        self.assertFalse(success)
        self.assertEqual(len(placed), 0)

    def test_products_do_not_overlap(self):
        # Pack 4 identical cubes in a 2x2 grid
        items = [
            ItemToPack(f'Cube {i}', Decimal('5'), Decimal('5'), Decimal('5'))
            for i in range(4)
        ]
        success, placed = PackingEngine.pack(
            box_length=Decimal('10'),
            box_width=Decimal('10'),
            box_height=Decimal('5'),
            items=items
        )
        self.assertTrue(success)
        self.assertEqual(len(placed), 4)

        # Check all pairs for overlap
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                p1 = placed[i]
                p2 = placed[j]
                self.assertFalse(
                    p1.overlaps_with(p2.x, p2.y, p2.z, p2.dx, p2.dy, p2.dz),
                    f"{p1} overlaps with {p2}"
                )

    def test_products_remain_within_box_boundaries(self):
        box_l, box_w, box_h = Decimal('15'), Decimal('12'), Decimal('8')
        items = [
            ItemToPack('Item 1', Decimal('7'), Decimal('6'), Decimal('4')),
            ItemToPack('Item 2', Decimal('8'), Decimal('5'), Decimal('4')),
        ]
        success, placed = PackingEngine.pack(box_l, box_w, box_h, items)
        self.assertTrue(success)
        for p in placed:
            self.assertGreaterEqual(p.x, Decimal('0'))
            self.assertGreaterEqual(p.y, Decimal('0'))
            self.assertGreaterEqual(p.z, Decimal('0'))
            self.assertLessEqual(p.x + p.dx, box_l)
            self.assertLessEqual(p.y + p.dy, box_w)
            self.assertLessEqual(p.z + p.dz, box_h)

    def test_duplicate_orientations_are_removed_when_dimensions_are_equal(self):
        # Equal on all 3 sides (cube)
        cube_orientations = PackingEngine.generate_orientations(
            Decimal('5'), Decimal('5'), Decimal('5')
        )
        self.assertEqual(len(cube_orientations), 1)
        self.assertEqual(cube_orientations, [(Decimal('5'), Decimal('5'), Decimal('5'))])

        # Square base (2 sides equal)
        square_base_orientations = PackingEngine.generate_orientations(
            Decimal('5'), Decimal('5'), Decimal('10')
        )
        self.assertEqual(len(square_base_orientations), 3)

        # All sides different
        general_orientations = PackingEngine.generate_orientations(
            Decimal('4'), Decimal('5'), Decimal('6')
        )
        self.assertEqual(len(general_orientations), 6)

    def test_product_quantity_is_correctly_considered(self):
        # A single 6x6x6 item fits in a 10x10x10 box, but two cannot
        item_single = [ItemToPack('Item', Decimal('6'), Decimal('6'), Decimal('6'))]
        self.assertTrue(PackingEngine.can_pack(Decimal('10'), Decimal('10'), Decimal('10'), item_single))

        items_double = [
            ItemToPack('Item', Decimal('6'), Decimal('6'), Decimal('6')),
            ItemToPack('Item', Decimal('6'), Decimal('6'), Decimal('6')),
        ]
        self.assertFalse(PackingEngine.can_pack(Decimal('10'), Decimal('10'), Decimal('10'), items_double))


class BoxSelectorTestCase(TestCase):
    """
    Unit tests for the BoxSelector recommendation service.
    """

    def setUp(self):
        self.product_small = Product.objects.create(
            name='Small Widget',
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            weight=Decimal('1.00')
        )

    def test_cheapest_suitable_box_is_selected(self):
        expensive_box = Box.objects.create(
            name='Expensive Box',
            length=Decimal('30.00'),
            width=Decimal('30.00'),
            height=Decimal('30.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('50.00'),
            is_active=True
        )
        cheap_box = Box.objects.create(
            name='Cheap Box',
            length=Decimal('30.00'),
            width=Decimal('30.00'),
            height=Decimal('30.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('20.00'),
            is_active=True
        )

        order = Order.objects.create(customer_name='Sarah')
        OrderItem.objects.create(order=order, product=self.product_small, quantity=1)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertTrue(result.success)
        self.assertEqual(result.box.id, cheap_box.id)
        self.assertEqual(result.box.cost, Decimal('20.00'))

    def test_more_expensive_suitable_boxes_rejected_in_favor_of_cheaper_ones(self):
        box_mid = Box.objects.create(
            name='Mid Box',
            length=Decimal('20.00'),
            width=Decimal('20.00'),
            height=Decimal('20.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('25.00'),
            is_active=True
        )
        box_large = Box.objects.create(
            name='Large Box',
            length=Decimal('50.00'),
            width=Decimal('50.00'),
            height=Decimal('50.00'),
            max_weight=Decimal('50.00'),
            cost=Decimal('80.00'),
            is_active=True
        )

        order = Order.objects.create(customer_name='Dave')
        OrderItem.objects.create(order=order, product=self.product_small, quantity=1)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertTrue(result.success)
        self.assertEqual(result.box.id, box_mid.id)
        self.assertNotEqual(result.box.id, box_large.id)

    def test_insufficient_weight_capacity(self):
        # Box fits dimensions but cannot support the weight
        Box.objects.create(
            name='Lightweight Box',
            length=Decimal('50.00'),
            width=Decimal('50.00'),
            height=Decimal('50.00'),
            max_weight=Decimal('2.00'),
            cost=Decimal('10.00'),
            is_active=True
        )
        heavy_product = Product.objects.create(
            name='Lead Ingot',
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            weight=Decimal('8.00')
        )

        order = Order.objects.create(customer_name='Heavy Order Customer')
        OrderItem.objects.create(order=order, product=heavy_product, quantity=1)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertFalse(result.success)
        self.assertIn("weight", result.error.lower())

    def test_insufficient_box_volume(self):
        # Box has volume 1000, order has 2 items of volume 1000 = 2000
        Box.objects.create(
            name='Tiny Box',
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            max_weight=Decimal('20.00'),
            cost=Decimal('5.00'),
            is_active=True
        )

        order = Order.objects.create(customer_name='Double Widget Customer')
        OrderItem.objects.create(order=order, product=self.product_small, quantity=2)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertFalse(result.success)

    def test_no_suitable_box_available(self):
        # No boxes created in DB
        order = Order.objects.create(customer_name='No Boxes Customer')
        OrderItem.objects.create(order=order, product=self.product_small, quantity=1)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertFalse(result.success)
        self.assertIn("available", result.error.lower())

    def test_inactive_boxes_are_ignored(self):
        # Cheaper box is inactive; active box is more expensive
        Box.objects.create(
            name='Inactive Cheap Box',
            length=Decimal('30.00'),
            width=Decimal('30.00'),
            height=Decimal('30.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('10.00'),
            is_active=False
        )
        active_box = Box.objects.create(
            name='Active Box',
            length=Decimal('30.00'),
            width=Decimal('30.00'),
            height=Decimal('30.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('35.00'),
            is_active=True
        )

        order = Order.objects.create(customer_name='Customer Active Only')
        OrderItem.objects.create(order=order, product=self.product_small, quantity=1)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertTrue(result.success)
        self.assertEqual(result.box.id, active_box.id)

    def test_equal_cost_boxes_use_smaller_volume_as_tie_breaker(self):
        # Box A volume = 27,000 cm3
        box_larger = Box.objects.create(
            name='Larger Volume Box',
            length=Decimal('30.00'),
            width=Decimal('30.00'),
            height=Decimal('30.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('25.00'),
            is_active=True
        )
        # Box B volume = 15,625 cm3
        box_smaller = Box.objects.create(
            name='Smaller Volume Box',
            length=Decimal('25.00'),
            width=Decimal('25.00'),
            height=Decimal('25.00'),
            max_weight=Decimal('10.00'),
            cost=Decimal('25.00'),
            is_active=True
        )

        order = Order.objects.create(customer_name='Tie Breaker Customer')
        OrderItem.objects.create(order=order, product=self.product_small, quantity=1)

        result = BoxSelector.recommend_box_for_order(order)
        self.assertTrue(result.success)
        self.assertEqual(result.box.id, box_smaller.id)

    def test_empty_orders_are_rejected(self):
        empty_order = Order.objects.create(customer_name='Empty Order')
        result = BoxSelector.recommend_box_for_order(empty_order)
        self.assertFalse(result.success)
        self.assertIn("no items", result.error.lower())


class RecommendationAPITestCase(APITestCase):
    """
    Integration tests for the Box Recommendation REST API endpoint:
    POST /api/orders/{id}/recommend-box/
    """

    def setUp(self):
        self.product = Product.objects.create(
            name='Coffee Mug',
            length=Decimal('12.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            weight=Decimal('0.50')
        )
        self.box_small = Box.objects.create(
            name='Small Box',
            length=Decimal('20.00'),
            width=Decimal('15.00'),
            height=Decimal('15.00'),
            max_weight=Decimal('5.00'),
            cost=Decimal('15.00'),
            is_active=True
        )
        self.box_large = Box.objects.create(
            name='Large Box',
            length=Decimal('50.00'),
            width=Decimal('50.00'),
            height=Decimal('50.00'),
            max_weight=Decimal('25.00'),
            cost=Decimal('40.00'),
            is_active=True
        )

    def test_successful_recommendation_api(self):
        order = Order.objects.create(customer_name='Alice')
        OrderItem.objects.create(order=order, product=self.product, quantity=1)

        url = f'/api/orders/{order.id}/recommend-box/'
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['order_id'], order.id)

        rec_box = response.data['recommended_box']
        self.assertEqual(rec_box['id'], self.box_small.id)
        self.assertEqual(rec_box['name'], 'Small Box')
        self.assertIn('dimensions', rec_box)
        self.assertEqual(rec_box['dimensions']['length'], 20)
        self.assertEqual(rec_box['dimensions']['width'], 15)
        self.assertEqual(rec_box['dimensions']['height'], 15)
        self.assertEqual(rec_box['cost'], 15)
        self.assertIn('actual_weight', rec_box)
        self.assertIn('reason', response.data)

    def test_no_suitable_box_response(self):
        giant_product = Product.objects.create(
            name='Giant Furniture',
            length=Decimal('200.00'),
            width=Decimal('100.00'),
            height=Decimal('80.00'),
            weight=Decimal('50.00')
        )
        order = Order.objects.create(customer_name='Big Order')
        OrderItem.objects.create(order=order, product=giant_product, quantity=1)

        url = f'/api/orders/{order.id}/recommend-box/'
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)

    def test_invalid_order_id(self):
        url = '/api/orders/99999/recommend-box/'
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('does not exist', response.data['error'])

    def test_recommendation_on_empty_order(self):
        order = Order.objects.create(customer_name='Empty Order')

        url = f'/api/orders/{order.id}/recommend-box/'
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('no items', response.data['error'])
