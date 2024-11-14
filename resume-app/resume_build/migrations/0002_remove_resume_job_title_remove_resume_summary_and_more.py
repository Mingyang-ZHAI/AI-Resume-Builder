# Generated by Django 5.1.3 on 2024-11-14 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume_build', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resume',
            name='job_title',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='summary',
        ),
        migrations.AddField(
            model_name='resume',
            name='education',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='experience',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='skills',
            field=models.TextField(blank=True, null=True),
        ),
    ]