# Generated by Django 5.2 on 2025-04-15 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MS", "0006_chat_recipient"),
    ]

    operations = [
        migrations.AddField(
            model_name="biddingproduct",
            name="notified",
            field=models.BooleanField(default=False),
        ),
    ]
