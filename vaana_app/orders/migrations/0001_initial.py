# Generated by Django 3.2.1 on 2021-05-28 10:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('carts', '0001_initial'),
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone_number', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True, help_text='Tell us anything we should know when delivering your order.')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='addresses.address')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number', models.CharField(db_index=True, max_length=128, unique=True)),
                ('currency', models.CharField(max_length=12)),
                ('total_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('shipping_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_prices', models.DecimalField(decimal_places=2, max_digits=12)),
                ('shipping_method', models.CharField(blank=True, max_length=128)),
                ('status', models.CharField(blank=True, max_length=100)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carts.cart')),
                ('shipping_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.shippingaddress')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
    ]
