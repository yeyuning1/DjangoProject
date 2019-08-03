#!/usr/bin/env python
#在当前环境中查找python解释器的路径

import os
import sys


def get_detail_html(sku):
    # 分类数据
    categories = get_categories()

    # 获取面包屑导航
    breadcrumb = get_breadcrumb(sku.category)

    # 获取spu
    spu = sku.spu

    # 获取规格信息：sku===>spu==>specs
    specs = spu.specs.order_by('id')

    # 查询所有的sku，如华为P10的所有库存商品
    skus = spu.skus.order_by('id')
    '''
    {
        选项:sku_id
    }
    说明：键的元组中，规格的索引是固定的
    示例数据如下：
    {
        (1,3):1,
        (2,3):2,
        (1,4):3,
        (2,4):4
    }
    '''
    sku_options = {}
    sku_option = []
    for sku1 in skus:
        infos = sku1.specs.order_by('spec_id')
        option_key = []
        for info in infos:
            option_key.append(info.option_id)
            # 获取当前商品的规格信息
            if sku.id == sku1.id:
                sku_option.append(info.option_id)
        sku_options[tuple(option_key)] = sku1.id

    # 遍历当前spu所有的规格
    specs_list = []
    for index, spec in enumerate(specs):
        option_list = []
        for option in spec.options.all():
            # 如果当前商品为蓝、64,则列表为[2,3]
            sku_option_temp = sku_option[:]
            # 替换对应索引的元素：规格的索引是固定的[1,3]
            sku_option_temp[index] = option.id
            # 为选项添加sku_id属性，用于在html中输出链接
            option.sku_id = sku_options.get(tuple(sku_option_temp), 0)
            # 添加选项对象
            option_list.append(option)
        # 为规格对象添加选项列表
        spec.option_list = option_list
        # 重新构造规格数据
        specs_list.append(spec)

    context = {
        'sku': sku,
        'categories': categories,
        'breadcrumb': breadcrumb,
        'category_id': sku.category_id,
        'spu': spu,
        'specs': specs_list
    }
    response = render(None, 'detail.html', context)
    return response.content.decode()


if __name__ == '__main__':
    sys.path.insert(0, '../')
    # 加载django配置
    os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"

    #将django环境生效
    import django

    django.setup()

    from django.conf import settings
    from django.shortcuts import render

    from meiduo_mall.utils.categories import get_categories
    from meiduo_mall.utils.breadcrumb import get_breadcrumb
    from goods.models import SKU

    # 查询所有商品数据
    skus = SKU.objects.all()
    # 遍历，逐个生成静态页面
    for sku in skus:
        # 生成html字符串
        html_str = get_detail_html(sku)
        # 文件路径
        file_name = os.path.join(settings.BASE_DIR, 'static/detail/%d.html' % sku.id)
        # 写文件
        with open(file_name, 'w') as f1:
            f1.write(html_str)

    print('ok')
