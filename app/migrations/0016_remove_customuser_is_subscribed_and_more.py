# Generated by Django 5.0.7 on 2025-02-22 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_customuser_free_plan_customuser_premium_plan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_subscribed',
        ),
        migrations.AddField(
            model_name='customuser',
            name='without_plan',
            field=models.BooleanField(default=False),
        ),
    ]
