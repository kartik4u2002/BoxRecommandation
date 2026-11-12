from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    API view to list orders or create a new order with items.
    POST /api/orders/ - Create an order
    GET /api/orders/ - List orders
    """
    queryset = Order.objects.prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer


class OrderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve an order by its ID.
    GET /api/orders/{id}/ - Retrieve order details
    """
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    lookup_field = 'pk'
