# Generated by Django 5.1.5 on 2025-04-28 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MS", "0017_remove_product_age_group_product_age_group"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="age_group",
        ),
        migrations.RemoveField(
            model_name="product",
            name="size",
        ),
        migrations.AddField(
            model_name="product",
            name="age_groups",
            field=models.ManyToManyField(blank=True, to="MS.agegroup"),
        ),
        migrations.AddField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(blank=True, to="MS.size"),
        ),
    ]
