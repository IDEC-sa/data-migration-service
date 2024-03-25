# Generated by Django 5.0.3 on 2024-03-14 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lineItem', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('unitPrice', models.PositiveIntegerField()),
                ('internalCode', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priceUnit', models.CharField(choices=[('SAR', 'Saudi Riyals'), ('USD', 'United States Dollar')])),
                ('csv', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='ProductList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('optional', models.BooleanField(default=False)),
                ('products', models.ManyToManyField(to='sales.product')),
            ],
        ),
    ]
