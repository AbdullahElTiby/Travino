# Generated by Django 5.0.7 on 2024-11-13 08:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_remove_audio_place'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteHotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotel_id', models.CharField(max_length=100)),
                ('hotel_name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_hotels', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'hotel_id')},
            },
        ),
    ]
