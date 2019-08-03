from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """属性text不可修改"""
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """用于搜索的表"""
        return SKU

    def index_queryset(self, using=None):
        """指定哪些行的数据在搜索范围内"""
        return self.get_model().objects.filter(is_launched=True)
