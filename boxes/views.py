from rest_framework import generics
from .models import Box
from .serializers import BoxSerializer


class BoxListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve the list of boxes or create a new box.
    GET /api/boxes/ - List all boxes
    POST /api/boxes/ - Create a new box
    """
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
