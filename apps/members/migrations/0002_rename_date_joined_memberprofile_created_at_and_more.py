# Generated by Django 5.0.4 on 2024-07-22 23:41

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="memberprofile",
            old_name="date_joined",
            new_name="created_at",
        ),
        migrations.RemoveField(
            model_name="memberprofile",
            name="stripe_account_id",
        ),
        migrations.RemoveField(
            model_name="memberprofile",
            name="stripe_customer_id",
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="instagram_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="latitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
            ),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="longitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
            ),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="member_bio",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="profile_photo_url",
            field=models.URLField(blank=True, max_length=2048),
        ),
        migrations.CreateModel(
            name="MemberPaymentDetails",
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
                (
                    "stripe_customer_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "stripe_account_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "member",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_details",
                        to="members.memberprofile",
                    ),
                ),
            ],
            options={
                "db_table": "member_payment_details",
            },
        ),
    ]