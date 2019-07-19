from django.shortcuts import render
from django.views import View


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        return render(request, 'list.html')
