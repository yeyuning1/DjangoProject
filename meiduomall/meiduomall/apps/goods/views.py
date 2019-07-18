from django.shortcuts import render
from django.views import View

from contents.models import ContentCategory
from goods.utils import get_categories


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告界面"""

        # 查询商品频道分类
        categories = get_categories()

        # 定义一个空字典
        dict = {}

        # 查询出所有的广告类别
        content_categories = ContentCategory.objects.all()

        for cat in content_categories:
            # 获取类别所对应的展示数据, 并对数据进行排序:
            # key:value  ==>  商品类别.key:具体的所有商品(排过序)
            dict[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 拼接参数
        context = {
            'categories': categories,
            'contents': dict
        }

        return render(request, 'index.html', context=context)
