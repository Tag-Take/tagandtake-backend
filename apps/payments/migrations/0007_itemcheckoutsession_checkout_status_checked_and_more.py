# Generated by Django 5.0.4 on 2024-10-09 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0006_remove_memberpaymentaccount_stripe_customer_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemcheckoutsession",
            name="checkout_status_checked",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="itempaymenttransaction",
            name="payment_status_checked",
            field=models.BooleanField(default=False),
        ),
    ]