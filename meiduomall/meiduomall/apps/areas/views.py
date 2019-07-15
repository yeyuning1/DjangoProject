import json
import re

from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views import View
import logging
from areas.models import Area, Address
from meiduomall.utils.response_code import RETCODE
from users.utils import LoginRequiredJSONMixin

logger = logging.getLogger('django')


class ProvinceAreasView(View):
    """省级地区"""

    def get(self, request):
        """提供省级地区数据
        1.查询省级数据
        2.序列化省级数据
        3.响应省级数据
        4.补充缓存逻辑
        """
        # 增加: 判断是否有缓存
        province_list = cache.get('province_list')

        if not province_list:
            # 1.查询省级数据
            try:
                province_model_list = Area.objects.filter(parent__isnull=True)

                # 2.序列化省级数据
                province_list = []
                for province_model in province_model_list:
                    province_list.append({'id': province_model.id,
                                          'name': province_model.name})

                # 增加: 缓存省级数据
                cache.set('province_list', province_list, 3600)
            except Exception as e:
                # DBERR: 5000
                return JsonResponse({'code': RETCODE.DBERR,
                                     'errmsg': '省份数据错误'})

        # 3.响应省级数据
        return JsonResponse({'code': RETCODE.OK,
                             'errmsg': 'OK',
                             'province_list': province_list})


class SubAreasView(View):
    """子级地区：市和区县"""

    def get(self, request, pk):
        """提供市或区地区数据
        1.查询市或区数据
        2.序列化市或区数据
        3.响应市或区数据
        4.补充缓存数据
        """
        # 判断是否有缓存
        sub_data = cache.get('sub_area_' + pk)

        if not sub_data:

            # 1.查询市或区数据
            try:
                sub_model_list = Area.objects.filter(parent=pk)
                parent_model = Area.objects.get(id=pk)  # 查询市或区的父级

                # 2.序列化市或区数据
                sub_list = []
                for sub_model in sub_model_list:
                    sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                sub_data = {
                    'id': parent_model.id,  # pk
                    'name': parent_model.name,
                    'subs': sub_list
                }

                # 缓存市或区数据
                cache.set('sub_area_' + pk, sub_data, 3600)
            except Exception as e:
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区县数据错误'})

        # 3.响应市或区数据
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})


class CreateAddressView(LoginRequiredJSONMixin, View):
    """新增地址"""

    def post(self, request):
        # 获取地址的个数
        count = request.user.addresses.count()
        # 判断是否超过地址上限：最多20个
        if count >= 20:
            return JsonResponse({'code': RETCODE.THROTTLINGERR,
                                 'errmsg': '超出地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')

        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            return JsonResponse({'code': RETCODE.DBERR,
                                 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '新增地址成功',
            'address': address_dict
        })
