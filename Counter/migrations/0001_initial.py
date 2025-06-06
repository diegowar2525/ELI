# Generated by Django 5.2.1 on 2025-05-13 00:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ruc', models.CharField(max_length=11, unique=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('file', models.FileField(upload_to='reportes/')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Counter.company')),
            ],
        ),
        migrations.CreateModel(
            name='TotalCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('word', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Counter.company')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Counter.report')),
            ],
        ),
    ]
