# Generated by Django 5.0.4 on 2024-09-18 20:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0002_alter_itemimages_item"),
    ]

    operations = [
        migrations.AlterField(
            model_name="itemimages",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="item",
                to="items.item",
            ),
        ),
    ]