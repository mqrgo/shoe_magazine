from django import template
from products.models import Brand, Type
from products.models import Cart, CartItem
from django.db.models import Sum

register = template.Library()

@register.simple_tag()
def get_products_by_brand():
    return Brand.objects.all()

@register.simple_tag()
def get_producs_by_type():
    return Type.objects.all()

@register.simple_tag(takes_context=True)
def get_cart(context):
    request = context['request']
    user = request.COOKIES.get('sessionid')
    if user is None:
        return 0
    cart = Cart.objects.get(user=user)
    total_count = cart.cart_items.aggregate(total=Sum('amount'))
    return total_count
    
@register.simple_tag(takes_context=True)
def is_user_authenticated(context):
    request = context['request']
    return request.user.is_authenticated
    