# Generated by Django 5.1.5 on 2025-03-07 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hisaab", "0004_remove_user_role_alter_user_userid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bill",
            name="id",
        ),
        migrations.RemoveField(
            model_name="category",
            name="id",
        ),
        migrations.RemoveField(
            model_name="product",
            name="id",
        ),
        migrations.RemoveField(
            model_name="report",
            name="id",
        ),
        migrations.AlterField(
            model_name="bill",
            name="billID",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="category",
            name="categoryID",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="product",
            name="productID",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="report",
            name="reportID",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
