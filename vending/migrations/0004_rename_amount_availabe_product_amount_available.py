# Generated by Django 4.0.2 on 2022-02-19 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vending', '0003_rename_balance_vendinguser_deposit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='amount_availabe',
            new_name='amount_available',
        ),
    ]
