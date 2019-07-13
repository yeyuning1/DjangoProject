from django.db import models


class BaseModel(models.Model):
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True,  # 创建或添加对象时自动添加时间, 修改或更新对象时, 不会更改时间
                                       verbose_name='创建时间')
    # 更新时间
    update_time = models.DateTimeField(auto_now=True,  # 凡是对对象进行操作(创建/添加/修改/更新),时间都会随之改变
                                       verbose_name='更新时间')

    class Meta:
        # 说明是个抽象类，抽象类不会创建数据表
        abstract = True
