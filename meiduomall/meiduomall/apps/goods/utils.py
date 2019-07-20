from collections import OrderedDict
from .models import GoodsChannel


def get_categories():
    """
    获取商城商品分类菜单
    :return 菜单字典
    """
    # 商品频道及分类菜单
    # 下面的代码生成的模板:
    # categories = {
    #  (1,  # 组1
    #       {'channels': [{'id': 1, 'name': '手机','url':'http://shouji.jd.com'},
    #                     {'id': 2, 'name': '相机','url':'http://www.itcast.cn'},
    #                     {'id': 3, 'name': '数码','url':'http://www.itcast.cn'}],
    #        'sub_cats': [ < GoodsCategory: 手机通讯 >,
    #                      < GoodsCategory: 手机配件 >,
    #                      < GoodsCategory: 摄影摄像 >,
    #                      < GoodsCategory: 数码配件 >,
    #                      < GoodsCategory: 影音娱乐 >,
    #                      < GoodsCategory: 智能设备 >,
    #                      < GoodsCategory: 电子教育 >
    #                    ]
    #       }
    #   ),(2, # 组2
    #        {
    #
    #   })
    # }

    # 第一部分: 从数据库中取数据:
    # 定义一个有序字典对象
    categories = OrderedDict()
    # 对 GoodsChannel 进行 group_id 和 sequence 排序, 获取排序后的结果:
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历排序后的结果: 得到所有的一级菜单( 即,频道 )
    for channel in channels:
        # 从频道中得到当前的 组id
        group_id = channel.group_id

        # 判断: 如果当前 组id 不在我们的有序字典中:
        if group_id not in categories:
            # 我们就把 组id 添加到 有序字典中
            # 并且作为 key值, value值 是 {'channels': [], 'sub_cats': []}
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 获取当前频道的分类名称
        cat1 = channel.category

        # 给刚刚创建的字典中, 追加具体信息:
        # 即, 给'channels' 后面的 [] 里面添加如下的信息:
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        # 根据 cat1 的外键反向, 获取下一级(二级菜单)的所有分类数据, 并遍历:
        for cat2 in cat1.goodscategory_set.all():
            # 创建一个新的列表:
            cat2.sub_cats = []
            # 根据 cat2 的外键反向, 获取下一级(三级菜单)的所有分类数据, 并遍历:
            for cat3 in cat2.goodscategory_set.all():
                # 拼接新的列表: key: 二级菜单名称, value: 三级菜单组成的列表
                cat2.sub_cats.append(cat3)
            # 所有内容在增加到 一级菜单生成的 有序字典中去:
            categories[group_id]['sub_cats'].append(cat2)

    return categories


def get_breadcrumb(category):
    """
    获取面包屑导航
    :param category: 商品类别
    :return: 面包屑导航字典
    """

    # 定义一个字典
    breadcrumb = dict(
        cat1='',
        cat2='',
        cat3=''
    )

    # 判断 category 是哪一个级别
    # 注意: 这里的 category 是 GoodsCategory 对象
    if category.parent is None:
        # 当前类别为一级类别
        breadcrumb['cat1'] = category
    # 因为这个表表示自关联, 关联对象还是自己
    elif category.goodscategory_set.count() == 0:
        # 当前类别为三级
        breadcrumb['cat3'] = category
        cat2 = category.parent
        breadcrumb['cat2'] = cat2
        breadcrumb['cat1'] = cat2.parent
    else:
        # 当前类别为二级
        breadcrumb['cat2'] = category
        breadcrumb['cat1'] = category.parent

    return breadcrumb


def get_goods_and_spec(sku_id, request):
    pass
