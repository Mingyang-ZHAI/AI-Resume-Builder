# Generated by Django 4.2.16 on 2024-11-24 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume_build', '0003_job_response'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='response',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
