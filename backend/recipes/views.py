from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from django.db.models import Q

from users.paginators import CustomNumberPagination
from users.permissions import IsOwnerOrReadOnlyForObject
from .models import IngredientInRecipe, Recipe, Tag
from .serializers import (
    IngrInRecipeSafeSerializer,
    RecipeSafeSerializer,
    RecipeUnsafeSerializer,
    TagSerializer,
)


class IngredientInRecipeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = IngrInRecipeSafeSerializer
    queryset = IngredientInRecipe.objects.select_related("ingredient")
    permission_classes = (AllowAny,)

    SearchFilter.search_param = "name"
    filter_backends = (SearchFilter,)
    search_fields = ("^name",)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomNumberPagination
    http_method_names = ("get", "post", "patch", "delete")
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnlyForObject,
    )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSafeSerializer
        return RecipeUnsafeSerializer

    def apply_query_param_filters(self, queryset):
        author = self.request.query_params.get("author")
        if author and author.isdigit():
            queryset = queryset.filter(Q(author=int(author)))

        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited and is_favorited == "1":
            queryset = queryset.filter(Q(in_favorites=self.request.user))

        is_in_cart = self.request.query_params.get("is_in_shopping_cart")
        if is_in_cart and is_in_cart == "1":
            queryset = queryset.filter(Q(in_baskets=self.request.user))

        tags = self.request.query_params.getlist("tags")
        if tags:
            filter_tags = Q(tags__slug=tags[0])
            for tag in tags[1:]:
                filter_tags = filter_tags | Q(tags__slug=tag)
            queryset = queryset.filter(filter_tags)

        return queryset

    def get_queryset(self):
        queryset = (
            Recipe.objects.select_related("author")
            .prefetch_related("ingredients__ingredient", "tags")
            .order_by("-pub_date")
        )
        if self.action == "list":
            queryset = self.apply_query_param_filters(queryset)
            return queryset
        return queryset
