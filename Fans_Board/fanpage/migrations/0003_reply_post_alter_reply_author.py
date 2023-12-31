# Generated by Django 4.1.5 on 2023-07-10 17:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanpage', '0002_alter_reply_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='post',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='fanpage.post'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='reply',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to=settings.AUTH_USER_MODEL),
        ),
    ]
