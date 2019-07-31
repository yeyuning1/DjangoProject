from rest_framework.viewsets import ModelViewSet

# class BookInfoViewSet(GenericAPIView):
#
#     queryset = BookInfo.objects.all()
#     serializer_class = BookInfoSerializer
#
#     def get(self, request):
#         list = self.get_queryset()
#         serializer = self.get_serializer(list, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# class HeroInfoViewSet(GenericAPIView):
#     queryset = HeroInfo.objects.all()
#     serializer_class = HeroInfoSerializer
#
#     def get(self, request, pk):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def put(self, request, pk):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, pk):
#         instance = self.get_object()
#         instance.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
from booktest.models import BookInfo
from booktest.serializers import BookInfoSerializer


class BookInfoViewSet(ModelViewSet):
    serializer_class = BookInfoSerializer
    queryset = BookInfo.objects.all()

