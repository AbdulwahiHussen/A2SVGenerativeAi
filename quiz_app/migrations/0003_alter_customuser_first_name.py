# Generated by Django 4.2.4 on 2023-09-03 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0002_customuser_carrier_customuser_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]