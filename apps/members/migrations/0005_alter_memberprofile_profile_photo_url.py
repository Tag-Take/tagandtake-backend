# Generated by Django 5.0.4 on 2024-07-25 07:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0004_delete_memberpaymentdetails"),
    ]

    operations = [
        migrations.AlterField(
            model_name="memberprofile",
            name="profile_photo_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]