# Generated by Django 3.0.7 on 2020-11-11 15:39

from django.db import migrations


def fill_price(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')

    for order_item in OrderItem.objects.select_related('product').all().iterator():
        order_item.price = order_item.product.price
        order_item.save()


class Migration(migrations.Migration):
    dependencies = [
        ('foodcartapp', '0038_orderitem_price'),
    ]

    operations = [
        migrations.RunPython(fill_price),
    ]