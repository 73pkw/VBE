# Generated by Django 3.2.1 on 2021-08-26 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shippings', '0001_initial'),
        ('carts', '0003_cart_owner'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='carts.cart'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.shippingaddress'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shippings.shippingmethod'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
    ]
