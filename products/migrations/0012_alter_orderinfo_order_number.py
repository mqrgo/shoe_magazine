# Generated by Django 5.0.4 on 2024-05-22 20:53

import products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_remove_orderinfo_cart_orderinfo_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='order_number',
            field=models.IntegerField(default=products.models.generate_order_number, editable=False, verbose_name='Номер заказа'),
        ),
    ]
