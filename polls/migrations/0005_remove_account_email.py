# Generated by Django 4.2.2 on 2023-07-09 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_account_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='email',
        ),
    ]
