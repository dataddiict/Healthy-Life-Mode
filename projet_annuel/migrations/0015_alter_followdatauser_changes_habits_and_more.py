# Generated by Django 5.0.4 on 2024-07-04 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projet_annuel', '0014_followdatauser_changes_habits_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followdatauser',
            name='Changes_Habits',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='followdatauser',
            name='Days_Indoors',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='followdatauser',
            name='Mental_Health_History',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='followdatauser',
            name='Social_Weakness',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='followdatauser',
            name='Work_Interest',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user_user',
            name='Changes_Habits',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user_user',
            name='Days_Indoors',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user_user',
            name='Mental_Health_History',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user_user',
            name='Social_Weakness',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user_user',
            name='Work_Interest',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Changes_Habits',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Days_Indoors',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Mental_Health_History',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Social_Weakness',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='Work_Interest',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
