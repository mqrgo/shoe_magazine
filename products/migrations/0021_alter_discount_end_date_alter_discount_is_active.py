# Generated by Django 5.0.4 on 2024-05-28 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='end_date',
            field=models.DateTimeField(verbose_name='Дата окончания'),
        ),
        migrations.AlterField(
            model_name='discount',
            name='is_active',
            field=models.BooleanField(editable=False, verbose_name='Активный'),
        ),
    ]
