# Generated by Django 5.1.5 on 2025-03-16 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hisaab", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="pdf_path",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
