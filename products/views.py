from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from products.models import Product, ProductImage, Stock, Brand, News, Cart, CartItem, OrderInfo, Discount
from products.utils import get_send_order_info, make_cart, last_check_items, create_payment
from django.db.models import Sum
from products.forms import UserOrder, OrderInfoAdminForm
from products.filters import ProductFilter
from products.send_email import send_user_email
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from products.decorators import is_user_staff



def index(request):
    products = Product.objects.all()[:3]
    news = News.objects.all()[:4]
    
    return render(
        request, 
        'products/index.html', {
            'products': products, 
            'news': news
            }
        )


def get_products_by_brand(request, brand_id):
    products = Product.objects.filter(brand__id=brand_id)
    f = ProductFilter(request.GET, queryset=products)
    brand_name = Brand.objects.get(id=brand_id).name
    return render(
        request, 
        'products/products_by_brand.html', {
            'filter': f, 
            'brand_name': brand_name
            }
        )


def details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    images = ProductImage.objects.filter(product=product).order_by('-image')
    stock = Stock.objects.filter(shoe=product)
    return render(
        request,
        'products/details.html',
        {
            'product': product,
            'images': images,
            'stock': stock,
        }
    )


def add_item_to_cart(request):
    next_url = request.POST.get('next_url', '/')
    article = request.POST.get('article')
    size = request.POST.get('size')
    user = request.COOKIES.get('sessionid')
    cart = Cart.objects.get(user=user)
    item_in_stock = Stock.objects.get(shoe__article=article, size=size)
    if CartItem.objects.filter(cart=cart, product=item_in_stock.shoe, size=size).exists():
        cart_item = CartItem.objects.get(cart=cart, product=item_in_stock.shoe, size=size)
        if cart_item.amount < item_in_stock.amount:
            cart_item.amount += 1
        cart_item.save()         
    else:
        CartItem.objects.create(
            cart=cart,
            product=item_in_stock.shoe,
            size=size,
            amount=1,         
        )
    return redirect(next_url)


def try_discount(request):
    promocode = request.GET.get('promocode')
    if not Discount.objects.filter(promocode=promocode).exists() or not Discount.objects.get(promocode=promocode).is_active:
        response = HttpResponseRedirect('/cart/?discount=no_exist')
        check_discount = request.session.get('promocode')
        if check_discount:
            del request.session['promocode']
    else:
        response = HttpResponseRedirect('/cart/?discount=success')
        request.session['promocode'] = promocode

    return response
            
        
def cart(request):

    discount_status = request.GET.get('discount')
    form = UserOrder()
    message = request.GET.get('message')
    user = request.COOKIES.get('sessionid')
    
    if user is None:
        return redirect('/')
    
    cart = Cart.objects.get(user=user)
    cart_items = cart.cart_items.all().order_by('id')
    total_value = cart_items.aggregate(total=Sum('amount')).get('total')
    total_price = 0
    cart = cart.user
    
    for item in cart_items: 
        total_price += item.product.price * item.amount
    total_price_with_delivery = total_price + 350
    total_price_with_discount = None
    promocode = request.session.get('promocode')
    if promocode and total_price != 0:
        discount_obj = Discount.objects.get(promocode=promocode)
        percent = discount_obj.percent if promocode else 0
        total_price_with_discount = total_price + 350 - (total_price * percent//100)
    return render(
        request, 
        'products/cart.html', {
            'cart_items': cart_items, 
            'total_value': total_value, 
            'total_price': total_price,
            'total_price_with_delivery': total_price_with_delivery, 
            'form': form, 
            'cart': cart,
            'message': message,
            'total_price_with_discount': total_price_with_discount,
            'discount_status': discount_status,
            }
        )


def delete_item_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect(reverse('products:cart'))


def edit_items_count_lower(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.amount > 1:
        item.amount -= 1
    item.save()
    return redirect(reverse('products:cart'))


def edit_items_count_upper(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    product = item.product
    item_in_stock = Stock.objects.get(shoe__article=product.article, size=item.size)
    if item.amount < item_in_stock.amount:
        item.amount += 1
        item.save()
    return redirect(reverse('products:cart'))


def success_order(request):
    if request.session.get('promocode'):
        del request.session['promocode']
    order_number = request.GET.get('order_number')
    if order_number:
        order = get_object_or_404(OrderInfo, order_number=order_number)
        if order.is_paid == True:
            return redirect(reverse('products:index'))
        order.is_paid = True
        order.cart.cart_items.all().delete()
        order.save()
        user_data = {field.name: getattr(order, field.name) for field in OrderInfo._meta.fields if field.name != 'user' and field.name != 'cart'}
        user_data['order_date'] = user_data['order_date'].isoformat()
        send_user_email.delay(user_data)
        return render(request, 'products/success_order.html')
    else:
        return HttpResponseServerError('error')

           
def form_order(request):
    cart = request.POST.get('cart')
    total_price = request.POST.get('total_price') 
    cart = Cart.objects.get(user=cart) 
    cart_items = cart.cart_items.all()
    
    last_check = last_check_items(cart_items) 
    form = UserOrder(request.POST) 
    
    if last_check is False or not form.is_valid():
        return redirect('/cart/?message=error')
    
    promocode = request.session.get('promocode')
    if promocode:
        if not Discount.objects.filter(promocode=promocode).exists() or not Discount.objects.get(promocode=promocode).is_active:
            del request.session['promocode']
            return redirect('/cart/?message=error')
    
    data = form.save(commit=False)
    data.order = make_cart(cart_items)
    data.cart = cart
    if request.user.is_authenticated:
        user = request.user
        data.user = user
    data.save()
    
    payment_id, confirmation_url = create_payment(total_price, data.order_number)
    if not payment_id or not confirmation_url:
        return HttpResponseServerError("Failed to create payment") 
    
    return HttpResponseRedirect(confirmation_url)
    

def track_your_order(requset):
    order_number = requset.GET.get('order_number')
    if order_number is None:
        data = None
    else:
        if OrderInfo.objects.filter(order_number=order_number).exists():
            order = OrderInfo.objects.get(order_number=order_number)
            tracking_number = order.tracking_number
            if tracking_number is None:
                data = 'exist'
            else:
                data = get_send_order_info(tracking_number)
        else:
            data = 'error'
    
    return render(requset, 'products/track_your_order.html', {'data': data})


def add_track_number(request):
    tracking_number = request.POST.get('tracking_number')
    order_number = request.POST.get('order_number')

    if not tracking_number is None:
        order = get_object_or_404(OrderInfo, order_number=order_number)
        order.delivery_status = OrderInfo.DeliveryStatus.SENT
        order.save()
    return redirect(reverse('users:lk'))


@is_user_staff
@login_required
def edit_order(request, order_number):
    order_info = get_object_or_404(OrderInfo, order_number=order_number)
    if request.method == 'POST':
        form = OrderInfoAdminForm(request.POST, instance=order_info)
        if form.is_valid:
            form.save()
            return redirect(reverse('users:lk'))
    else:
        order_info = get_object_or_404(OrderInfo, order_number=order_number)
        form = OrderInfoAdminForm(instance=order_info)
    return render(request, 'products/edit_order.html', {'form': form, 'order_number': order_number})


