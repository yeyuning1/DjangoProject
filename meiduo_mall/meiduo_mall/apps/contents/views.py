from django.shortcuts import render
from django.views import View
from goods.models import GoodsCategory, GoodsChannel
from .models import ContentCategory, Content
from meiduo_mall.utils.categories import get_categories

class IndexView(View):
    def get(self, request):
        #查询分类
        categories=get_categories()

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

        return render(request, 'index.html', context=context)
