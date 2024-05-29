from django.urls import path
from products import views
from django.views.decorators.cache import cache_page

app_name = 'products'

urlpatterns = [
    path('', views.index, name='index'),
    path('products_by_brand/<int:brand_id>', views.get_products_by_brand, name='products_by_brand'),
    path('details/<slug:slug>', views.details, name='details'),
    path('add_item_to_cart', views.add_item_to_cart, name='add_item_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('delete_item_from_cart/<int:item_id>/', views.delete_item_from_cart, name='delete_item_from_cart'),
    path('edit_items_count_lower/<int:item_id>/', views.edit_items_count_lower, name='edit_items_count_lower'),
    path('edit_items_count_upper/<int:item_id>/', views.edit_items_count_upper, name='edit_items_count_upper'),
    path('edit_order/<int:order_number>', views.edit_order, name='edit_order'),
    path('form_order/', views.form_order, name='form_order'),
    path('track_your_order/', views.track_your_order, name='track_your_order'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('success_order/', views.success_order, name='success_order'),
    path('try_discount/', views.try_discount, name='try_discount'),
    
    path('testtest/', views.testtest)
]

