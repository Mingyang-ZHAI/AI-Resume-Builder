# Generated by Django 4.2.16 on 2024-11-19 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume_build', '0006_rename_month_education_end_month_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='bullet_points',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='experience',
            name='department_and_role',
            field=models.TextField(default='Not Specified'),
        ),
        migrations.AddField(
            model_name='experience',
            name='institution_name',
            field=models.CharField(default='Unknown Institution', max_length=200),
        ),
        migrations.AddField(
            model_name='experience',
            name='position',
            field=models.CharField(default='Unknown Position', max_length=100),
        ),
        migrations.AlterField(
            model_name='education',
            name='end_month',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='education',
            name='end_year',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='education',
            name='start_month',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='education',
            name='start_year',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='experience',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='end_month',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='experience',
            name='end_year',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='experience',
            name='start_month',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='experience',
            name='start_year',
            field=models.IntegerField(),
        ),
    ]