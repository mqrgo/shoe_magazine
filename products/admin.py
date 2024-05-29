from django.contrib import admin
from products import models
# Register your models here.

@admin.register(models.OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'delivery_status', 'name', 'phone', 'email', 'order_date', 'tracking_number']

    
class CartItemInline(admin.TabularInline):
    model = models.CartItem
    extra = 1


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']
    inlines = [
        CartItemInline,
    ]


@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'published']


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(models.Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name']


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'article', 'gender', 'slug', 'is_publish']
    inlines = [
        ProductImageInline,
    ]


@admin.register(models.Stock)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['shoe', 'size', 'amount']
    ordering = ['shoe']


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['promocode', 'percent', 'is_active', 'end_date']