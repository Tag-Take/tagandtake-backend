# Generated by Django 5.0.4 on 2024-08-01 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_remove_storeprofile_active_tags_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeprofile',
            name='shop_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]