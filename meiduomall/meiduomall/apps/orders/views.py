from django.shortcuts import render
from django.views import View


class OrderSettlementView(View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        return render(request, 'place_order.html')
