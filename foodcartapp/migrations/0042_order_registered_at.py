# Generated by Django 3.0.7 on 2020-11-13 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='registered_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]