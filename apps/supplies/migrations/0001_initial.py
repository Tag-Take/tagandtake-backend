# Generated by Django 5.0.4 on 2024-09-29 15:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("payments", "0001_initial"),
        ("stores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StoreSupply",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stripe_price_id", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Store Supply",
                "verbose_name_plural": "Store Supplies",
                "db_table": "store_supplies",
            },
        ),
        migrations.CreateModel(
            name="SupplyCheckoutItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("item_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "checkout_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="payments.suppliescheckoutsession",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stores.storeprofile",
                    ),
                ),
                (
                    "supply",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="supplies.storesupply",
                    ),
                ),
            ],
            options={
                "verbose_name": "Supply Checkout Item",
                "verbose_name_plural": "Supply Checkout Items",
                "db_table": "supply_checkout_items",
            },
        ),
        migrations.CreateModel(
            name="SupplyOrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField()),
                ("item_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="supply_order",
                        to="payments.suppliespaymenttransaction",
                    ),
                ),
                (
                    "supply",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="supplies.storesupply",
                    ),
                ),
            ],
            options={
                "verbose_name": "Supply Order Item",
                "verbose_name_plural": "Supply Order Items",
                "db_table": "supply_order_items",
            },
        ),
    ]