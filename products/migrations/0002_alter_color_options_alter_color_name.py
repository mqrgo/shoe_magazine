# Generated by Django 5.0.4 on 2024-05-16 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='color',
            options={'ordering': ['name'], 'verbose_name': 'Цвет', 'verbose_name_plural': 'Цвета'},
        ),
        migrations.AlterField(
            model_name='color',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Цвет'),
        ),
    ]
