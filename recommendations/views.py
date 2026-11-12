from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from orders.models import Order
from .services.box_selector import BoxSelector
from .serializers import RecommendedBoxDetailSerializer


class RecommendBoxView(APIView):
    """
    POST /api/orders/{id}/recommend-box/
    Evaluates available shipping boxes and recommends the most suitable,
    cost-effective box for the specified order.
    """

    def post(self, request, pk=None, order_id=None):
        target_id = pk if pk is not None else order_id
        try:
            order = Order.objects.prefetch_related('items__product').get(pk=target_id)
        except Order.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "order_id": target_id,
                    "error": f"Order with ID {target_id} does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        result = BoxSelector.recommend_box_for_order(order)

        if not result.success:
            return Response(
                {
                    "success": False,
                    "order_id": order.id,
                    "error": result.error
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        box_serializer = RecommendedBoxDetailSerializer(
            result.box,
            context={'actual_weight': result.actual_weight}
        )

        return Response(
            {
                "success": True,
                "order_id": order.id,
                "recommended_box": box_serializer.data,
                "reason": result.reason
            },
            status=status.HTTP_200_OK
        )
