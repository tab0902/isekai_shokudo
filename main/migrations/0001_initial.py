# Generated by Django 2.0.2 on 2018-07-01 16:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.CharField(blank=True, max_length=255, verbose_name='ユーザーID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='メニュー名')),
                ('description', models.TextField(blank=True, verbose_name='説明文')),
                ('price', models.IntegerField(blank=True, null=True, verbose_name='値段')),
                ('image_path', models.ImageField(blank=True, null=True, upload_to='img/post/', verbose_name='画像')),
                ('status', models.SmallIntegerField(verbose_name='ステータス')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': '投稿',
                'verbose_name_plural': '投稿',
                'db_table': 'posts',
            },
        ),
    ]
