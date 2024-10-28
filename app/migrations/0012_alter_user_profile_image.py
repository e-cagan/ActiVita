# Generated by Django 5.0.4 on 2024-10-09 17:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0011_alter_user_profile_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="profile_image",
            field=models.ImageField(
                blank=True, default="app/img/default_profile.jpg", upload_to="img/"
            ),
        ),
    ]
