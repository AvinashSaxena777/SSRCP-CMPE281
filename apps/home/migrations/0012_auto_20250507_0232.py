# Generated by Django 3.2.6 on 2025-05-07 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_auto_20250507_0220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='alert_latitude',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='alert',
            name='alert_longitude',
            field=models.FloatField(default=None),
        ),
    ]
