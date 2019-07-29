from django.db import models


# models.py
class BookInfo(models.Model):
    """图书模型类"""
    btitle = models.CharField(max_length=20, verbose_name='标题')
    bpub_date = models.DateField(verbose_name='发布日期')
    bread = models.IntegerField(default=0, verbose_name='阅读量')
    bcomment = models.IntegerField(default=0, verbose_name='评论量')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        db_table = 'tb_books'
        verbose_name = '图书'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.btitle


class HeroInfo(models.Model):
    """英雄模型类"""
    GENDER_CHOICES = (
        (0, '男'),
        (1, '女')
    )
    hname = models.CharField(max_length=20, verbose_name='名称')
    hgender = models.SmallIntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别')
    hcomment = models.CharField(max_length=200, null=True, verbose_name='备注')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')
    hbook = models.ForeignKey('BookInfo', on_delete=models.CASCADE, verbose_name='所属图书')

    class Meta:
        db_table = 'tb_heros'
        verbose_name = '英雄'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hname
