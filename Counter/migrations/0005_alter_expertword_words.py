# Generated by Django 5.2.1 on 2025-06-09 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Counter', '0004_word_remove_expertword_word_expertword_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expertword',
            name='words',
            field=models.ManyToManyField(blank=True, null=True, related_name='words', to='Counter.word'),
        ),
    ]
