# Generated by Django 3.2.25 on 2024-07-27 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mypage',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='friends_with', to='accounts.Mypage'),
        ),
    ]
