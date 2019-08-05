from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsVisitSerializer
from users.models import User


class UserTotalCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取网站总用户数:
        1. 获取网站总用户数量
        2. 返回应答
        """
        now_date = timezone.now()
        count = User.objects.count()
        response_data = {
            "count": count,
            "date": now_date.date()
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserDayIncrementView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = timezone.now().replace(hour=0, minute=0, second=0)
        count = User.objects.filter(date_joined__gte=now_date).count()

        response_data = {
            'date': now_date.date(),
            'count': count
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserDayActiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(last_login__gte=now_date).count()

        response_data = {
            'date': now_date.date(),
            'count': count
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserDayOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(orders__create_time__gte=now_date).distinct().count()

        response_data = {
            'date': now_date.date(),
            'count': count
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserMonthCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        begin_date = now_date - timezone.timedelta(days=29)

        current_date = begin_date

        month_li = []

        while current_date < now_date:
            next_date = current_date + timezone.timedelta(days=1)

            count = User.objects.filter(date_joined__gte=current_date,
                                        date_joined__lt=next_date).count()
            month_li.append({
                'date': current_date.date(),
                'count': count
            })
            current_date = next_date
        return Response(month_li, status=status.HTTP_200_OK)


class GoodsDayView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = timezone.now().date()
        goods_visit = GoodsVisitCount.objects.filter(date=now_date)
        serializer = GoodsVisitSerializer(goods_visit, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
