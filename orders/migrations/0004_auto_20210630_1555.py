# Generated by Django 3.1.6 on 2021-06-30 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
        ('orders', '0003_auto_20210630_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='variation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.variation'),
        ),
    ]
