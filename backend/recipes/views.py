from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)

    SearchFilter.search_param = "name"
    filter_backends = (SearchFilter,)
    search_fields = ("^name",)