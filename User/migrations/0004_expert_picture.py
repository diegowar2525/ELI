# Generated by Django 5.2.1 on 2025-06-05 22:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0003_remove_expert_picture_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='picture',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expert_picture', to='User.userprofile'),
        ),
    ]
