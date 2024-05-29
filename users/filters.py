import django_filters
from products.models import OrderInfo

class OrderInfoFilter(django_filters.FilterSet):
    
    class Meta:
        model = OrderInfo
        fields = ['order_number', 'delivery_status']