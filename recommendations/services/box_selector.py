from decimal import Decimal
from typing import Optional, List
from boxes.models import Box
from orders.models import Order
from .packing_engine import PackingEngine, ItemToPack


class RecommendationResult:
    """
    Data container holding the result of a box recommendation request.
    """
    def __init__(
        self,
        success: bool,
        box: Optional[Box] = None,
        reason: str = "",
        error: Optional[str] = None,
        actual_weight: Decimal = Decimal('0.00'),
        total_volume: Decimal = Decimal('0.00'),
    ):
        self.success = success
        self.box = box
        self.reason = reason
        self.error = error
        self.actual_weight = actual_weight
        self.total_volume = total_volume


class BoxSelector:
    """
    Service responsible for selecting the optimal shipping box for an order.

    Selection Workflow:
    1. Retrieve and aggregate all order items (accounting for quantities).
    2. Compute total weight and combined product volume.
    3. Filter active boxes by weight capacity and minimum required volume.
    4. Run 3D packing validation on candidate boxes.
    5. Sort feasible boxes by:
       - Cost (ascending)
       - Volume (ascending, tie-breaker for identical cost)
    6. Return the cheapest suitable box or an informative failure explanation.
    """

    @classmethod
    def recommend_box_for_order(
        cls,
        order: Order,
        available_boxes: Optional[List[Box]] = None
    ) -> RecommendationResult:
        """
        Evaluate available boxes and recommend the cheapest box that can
        physically fit and support the order.
        """
        # Step 1: Calculate order requirements
        items = list(order.items.select_related('product').all())
        if not items:
            return RecommendationResult(
                success=False,
                error="Cannot recommend a box for an order with no items."
            )

        items_to_pack: List[ItemToPack] = []
        total_weight = Decimal('0.00')
        total_volume = Decimal('0.00')

        for order_item in items:
            product = order_item.product
            for _ in range(order_item.quantity):
                item = ItemToPack(
                    name=product.name,
                    length=product.length,
                    width=product.width,
                    height=product.height,
                    weight=product.weight,
                    product_id=product.id,
                )
                items_to_pack.append(item)
                total_weight += product.weight
                total_volume += item.volume

        # Step 2: Retrieve candidate boxes
        if available_boxes is None:
            boxes_queryset = Box.objects.filter(is_active=True)
        else:
            boxes_queryset = [b for b in available_boxes if b.is_active]

        if not boxes_queryset:
            return RecommendationResult(
                success=False,
                error="No active shipping boxes are currently available.",
                actual_weight=total_weight,
                total_volume=total_volume
            )

        # Preliminary filter: weight and volume
        candidate_boxes = []
        for box in boxes_queryset:
            if box.max_weight < total_weight:
                continue
            if box.volume < total_volume:
                continue
            candidate_boxes.append(box)

        if not candidate_boxes:
            return RecommendationResult(
                success=False,
                error="No available box has sufficient weight capacity or volume for this order.",
                actual_weight=total_weight,
                total_volume=total_volume
            )

        # Step 4: 3D packing validation across candidates
        feasible_boxes: List[Box] = []
        for box in candidate_boxes:
            fits = PackingEngine.can_pack(
                box_length=box.length,
                box_width=box.width,
                box_height=box.height,
                items=items_to_pack
            )
            if fits:
                feasible_boxes.append(box)

        if not feasible_boxes:
            return RecommendationResult(
                success=False,
                error="No available box can physically accommodate the dimensions of the items in this order.",
                actual_weight=total_weight,
                total_volume=total_volume
            )

        # Step 5: Select the recommended box
        # Sort by: 1) Cost (ascending), 2) Volume (ascending, tie-breaker), 3) ID
        feasible_boxes.sort(key=lambda b: (b.cost, b.volume, b.id))
        best_box = feasible_boxes[0]

        return RecommendationResult(
            success=True,
            box=best_box,
            reason="Lowest-cost box satisfying weight and packing requirements.",
            actual_weight=total_weight,
            total_volume=total_volume
        )
