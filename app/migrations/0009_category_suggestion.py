# Generated by Django 5.0.7 on 2024-11-29 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_remove_category_suggestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='suggestion',
            field=models.TextField(default='Etc.'),
        ),
    ]
