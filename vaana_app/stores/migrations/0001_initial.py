<<<<<<< HEAD
# Generated by Django 3.2.1 on 2021-05-27 10:56

from django.db import migrations, models
=======
# Generated by Django 3.2.1 on 2021-05-26 09:52

from django.db import migrations, models
import uuid
>>>>>>> develop


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('store_address', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
