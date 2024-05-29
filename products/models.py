from django.db import models
from django.urls import reverse
from slugify import slugify
from django.utils import timezone
from random import randint
import json
from django.contrib.auth.models import User



def generate_articul():
    while True:
        article = randint(10_000, 1_000_000)
        if not Product.objects.filter(article=article).exists():
            return article


def generate_image_path(instance, filename):
    return f'product_image/{instance.product.slug}/{filename}'


def generate_empty_json():
    return json.dumps({})


def generate_order_number():
    while True:
        order_number = randint(10_000, 99_999)
        if not OrderInfo.objects.filter(order_number=order_number).exists():
            return order_number


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Цвет')
    
    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Тип')
    
    class Meta:
        verbose_name = 'Тип'
        verbose_name_plural = 'Тип'
        ordering = ['name']
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:products_by_type', args=[self.id])


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название', unique=True)
    
    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:products_by_brand', args=[self.id])
    

class Product(models.Model):
    class Gender(models.TextChoices):
        MAN = 'MAN', 'Мужские'
        WOMAN = 'WMN', 'Женские'
        UNI = 'UNI', 'Унисекс'

    class Season(models.TextChoices):
        WINTER = 'WN', 'Зима'
        SUMMER = 'SM', 'Лето'
        AUT_SPR = 'AS', 'Весна/Осень'
        
    title = models.CharField(max_length=255, verbose_name='Название товара')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name='product', verbose_name='Бренд')
    gender = models.CharField(max_length=3, choices=Gender.choices, default=Gender.UNI, verbose_name='Пол')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, default=None, null=True,blank=True, related_name='product', verbose_name='Цвет')
    product_type = models.ForeignKey(Type, on_delete=models.SET_NULL, default=None, null=True, blank=True, related_name='product', verbose_name='Тип')
    season = models.CharField(max_length=2, choices=Season.choices, default=Season.SUMMER, verbose_name='Сезон')
    article = models.PositiveIntegerField(unique=True, verbose_name='Артикул', editable=False)
    price = models.PositiveIntegerField(verbose_name='Стоимость')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    published = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True, verbose_name='Слаг', editable=False, null=True)
    is_publish = models.BooleanField(verbose_name='Опубликовано', default=False)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-published']
        indexes = [
            models.Index(fields=['article'])
        ]

    def __str__(self):
        return f'{self.brand} - {self.title}'

    def save(self, *ar, **kw):
        self.article = generate_articul()
        self.slug = slugify(f'{self.brand}-{self.title}-{str(self.article)}')
        super().save(*ar, **kw)

    def get_absolute_url(self):
        return reverse("products:details", args=[self.slug])


class Stock(models.Model):
    size = models.PositiveSmallIntegerField(verbose_name='Размер')
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')
    shoe = models.ForeignKey(Product, related_name='stock', verbose_name='Обувь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склад'
        ordering = ['size']
        unique_together = ['shoe', 'size']

    def __str__(self):
        return f'{self.shoe}. Size {self.size}'
    
    def get_max_amount(self):
        return self.amount


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='image', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=generate_image_path)


class Cart(models.Model):
    user = models.CharField(max_length=255, verbose_name='Пользователь')
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        
    def __str__(self):
        return f'Корзина пользователя {self.user}'
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.PositiveSmallIntegerField(verbose_name='Размер')
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')
    
    def __str__(self):
        return f'{self.product} x {self.size} x {self.amount}'
    

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    cover = models.ImageField(verbose_name='Кавер', upload_to='news_covers/%Y/%m/%d')
    body = models.TextField(verbose_name='Текст')
    published = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')    
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default='Anonym', related_name='news')
    slug = models.SlugField(verbose_name='Слаг', unique_for_date='published', editable=False, null=True)
    
    class Meta:
        ordering = ['-published']
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'
        
    def __str__(self):
        return self.title
    
    def save(self, *ar, **kw):
        self.slug = slugify(self.title)
        super().save(*ar, **kw)


class OrderInfo(models.Model):
    class DeliveryStatus(models.TextChoices):
        FORMED = 'FM', 'Сформирован'
        SENT = 'ST', 'Отправлен'
        RECEIVED = 'RC', 'Получен'
    
    class DeliveryChoices(models.TextChoices):
        CDEK = 'CD', 'CDEK'
        POST_OFFICE = 'PO', 'Почта России'
    
    order_number = models.IntegerField(verbose_name='Номер заказа', default=generate_order_number, editable=False)
    email = models.EmailField(verbose_name='Email')
    name = models.CharField(verbose_name='ФИО')
    phone = models.CharField(verbose_name='Номер телефона', max_length=12)
    address = models.CharField(verbose_name='Адрес', max_length=255)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    order_date = models.DateTimeField(default=timezone.now, verbose_name='Дата заказа')
    delivery_type = models.CharField(max_length=2, choices=DeliveryChoices.choices, default=DeliveryChoices.POST_OFFICE, verbose_name='Доставка')
    tracking_number = models.CharField(max_length=100, null=True, blank=True, default=None, verbose_name='Трек номер')
    delivery_status = models.CharField(max_length=2, choices=DeliveryStatus.choices, default=DeliveryStatus.FORMED, verbose_name='Статус заказа')
    order = models.JSONField(verbose_name='Детали заказа', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_info', null=True, blank=True, default=None)
    is_paid = models.BooleanField(verbose_name='Оплачено', default=False)
    cart = models.ForeignKey(Cart, related_name='order_info', on_delete=models.SET_NULL, null=True, blank=True)
    in_archive = models.BooleanField(verbose_name='В архиве', null=True, default=False)
    
    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Информация о заказе'
        verbose_name_plural = 'Информация о заказах'
        
    def __str__(self):
        return f'Заказ №{self.order_number}'
    
    def save(self, *ar, **kw):
        if self.tracking_number and self.delivery_status != OrderInfo.DeliveryStatus.RECEIVED:
            self.delivery_status = OrderInfo.DeliveryStatus.SENT
        super().save(*ar, **kw)
    

class Discount(models.Model):
    promocode = models.CharField(verbose_name='Промокод', max_length=30)
    percent = models.PositiveSmallIntegerField(verbose_name='Процент')
    is_active = models.BooleanField(editable=False, verbose_name='Активный')
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
    
    def check_status(self):
        if self.end_date < timezone.now():
            self.is_active = False
            return False
        return True
    
    def save(self, *ar, **kw):
        self.is_active = True if self.check_status() else False
        super().save(*ar, **kw)