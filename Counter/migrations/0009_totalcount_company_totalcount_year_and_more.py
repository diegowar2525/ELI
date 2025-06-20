# Generated by Django 5.2.1 on 2025-06-18 20:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Counter', '0008_delete_totalglobalcount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalcount',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Counter.company'),
        ),
        migrations.AddField(
            model_name='totalcount',
            name='year',
            field=models.PositiveIntegerField(default=2020),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='totalcount',
            name='word',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='totalcount',
            unique_together={('year', 'word', 'company')},
        ),
    ]
