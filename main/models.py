import uuid
from django.db import models

# Create your models here.

class UUIDModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class Post(UUIDModel):
    user_id = models.CharField(verbose_name='ユーザーID', max_length=255, blank=True)
    title = models.CharField(verbose_name='メニュー名', max_length=255, blank=True)
    description = models.TextField(verbose_name='説明文', blank=True)
    price = models.IntegerField(verbose_name='値段', blank=True, null=True)
    image_path = models.ImageField(verbose_name='画像', upload_to='img/post/', blank=True, null=True)
    status = models.SmallIntegerField(verbose_name='ステータス')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        db_table = 'posts'
        verbose_name = '投稿'
        verbose_name_plural = '投稿'

    def __str__(self):
        return '%s' % self.title
