# Generated by Django 5.0.3 on 2024-03-20 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0015_rename_date_quoterequest_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='quoterequest',
            name='contractReference',
            field=models.CharField(default='ref', max_length=50),
            preserve_default=False,
        ),
    ]
