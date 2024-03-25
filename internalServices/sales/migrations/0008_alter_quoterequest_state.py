# Generated by Django 5.0.3 on 2024-03-17 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_alter_quoterequest_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quoterequest',
            name='state',
            field=models.CharField(choices=[('val', 'Validated'), ('nval', 'Not Validated'), ('app', 'Approved'), ('napp', 'Not Approved')], max_length=4),
        ),
    ]
