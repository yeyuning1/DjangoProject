from collections import OrderedDict
from goods.models import GoodChannel


def get_categories():
    """
    获取商城商品分类菜单
    :return: 菜单字典
    """
    # 商品频道及分类菜单
    # 下面的代码生成的模板
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
    # 对 GoodsChannel 进行 group_id 和 sequence 排序, 获取排序后的结果
    channels = GoodChannel.objects.order_by('group_id', 'sequence')
    # 遍历排序后的结果: 得到所有的一级菜单( 即,频道 )
    for channel in channels:
        # 从频道中得到当前的 组id
        group_id = channel.group_id

        # 如果当前组 id 不在有序字典中
        if group_id not in categories:
            # 把组 id 添加到有序字典中
            # 作为key值，并且 value值是{'channels': [], 'sub_cats': []}
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
        # 自连接查询
        # 根据 cat1 的外键反向, 获取下一级(二级菜单)的所有分类数据, 并遍历:
        for cat2 in cat1.goodscategory_set.all():
            # 创建一个新的列表
            cat2.sub_cats = []
            # 根据 cat2 的外键反向, 获取下一级(三级菜单)的所有分类数据, 并遍历:
            for cat3 in cat2.goodscategory_set.all():
                # 拼接新的列表: key: 二级菜单名称, Value:三级菜单组成的列表
                cat2.sub_cats.append(cat3)

            # 所有的内容增加到以及菜单生成的有序字典中去：
            categories[group_id]['channel'].append(cat2)

    return categories
