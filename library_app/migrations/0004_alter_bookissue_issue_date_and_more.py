# Generated by Django 5.1.6 on 2025-03-13 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0003_bookrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookissue',
            name='issue_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='bookissue',
            name='return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
