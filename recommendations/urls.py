from django.urls import path
from .views import RecommendBoxView

urlpatterns = [
    path('orders/<int:pk>/recommend-box/', RecommendBoxView.as_view(), name='recommend-box'),
]
