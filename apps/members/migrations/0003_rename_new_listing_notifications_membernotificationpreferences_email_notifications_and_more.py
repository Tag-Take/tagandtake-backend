# Generated by Django 5.0.4 on 2024-07-23 00:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0002_rename_date_joined_memberprofile_created_at_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="membernotificationpreferences",
            old_name="new_listing_notifications",
            new_name="email_notifications",
        ),
        migrations.RenameField(
            model_name="membernotificationpreferences",
            old_name="sale_notifications",
            new_name="mobile_notifications",
        ),
        migrations.AddField(
            model_name="membernotificationpreferences",
            name="mobile",
            field=models.CharField(blank=True, max_length=15),
        ),
    ]