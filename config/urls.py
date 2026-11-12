"""
URL configuration for box_selection_system project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('products.urls')),
    path('api/boxes/', include('boxes.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/', include('recommendations.urls')),
]
