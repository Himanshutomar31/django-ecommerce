# Generated by Django 3.2.9 on 2021-11-12 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=180, unique=True),
        ),
    ]
