from django.shortcuts import render
from .models import ContentCategory
from meiduo_mall.utils.categories import get_categories
from django.conf import settings
import os


def generate_index_html():
    # 1.生成html
    # 查询分类
    categories = get_categories()

    # 查询广告数据
    content_category_list = ContentCategory.objects.all()
    # 构造广告字典
    '''
    {广告位标识：[广告1,....]}
    '''
    contents = {}
    for content_category in content_category_list:
        contents[content_category.key] = content_category.content_set.order_by('sequence')

    context = {
        'categories': categories,
        'contents': contents
    }

    response = render(None, 'index.html', context=context)
    html_str = response.content.decode()

    # 写文件
    with open(os.path.join(settings.BASE_DIR, 'static/index.html'), 'w') as f:
        f.write(html_str)
