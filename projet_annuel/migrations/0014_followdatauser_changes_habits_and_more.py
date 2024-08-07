# Generated by Django 5.0.4 on 2024-07-04 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projet_annuel', '0013_remove_followdatauser_caec_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='followdatauser',
            name='Changes_Habits',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='followdatauser',
            name='Days_Indoors',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='followdatauser',
            name='Mental_Health_History',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='followdatauser',
            name='Social_Weakness',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='followdatauser',
            name='Work_Interest',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_user',
            name='Changes_Habits',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_user',
            name='Days_Indoors',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_user',
            name='Mental_Health_History',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_user',
            name='Social_Weakness',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_user',
            name='Work_Interest',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='Changes_Habits',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='Days_Indoors',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='Mental_Health_History',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='Social_Weakness',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='Work_Interest',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
