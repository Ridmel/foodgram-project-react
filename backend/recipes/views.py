from rest_framework import mixins, status, validators, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from django.db.models import Q
from django.shortcuts import get_object_or_404

from users.paginators import CustomNumberPagination
from users.permissions import IsOwnerOrReadOnlyForObject
from .models import IngredientInRecipe, Recipe, Tag
from .serializers import (
    IngrInRecipeSafeSerializer,
    RecipeSafeSerializer,
    RecipeShortPresentSerializer,
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

    def get_permissions(self):
        if self.action == "favorite":
            return (IsAuthenticated(),)
        return IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnlyForObject()

    def get_serializer_class(self):
        if self.action == "favorite":
            return RecipeShortPresentSerializer
        if self.action in ("list", "retrieve"):
            return RecipeSafeSerializer
        return RecipeUnsafeSerializer

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

    @action(detail=True, methods=("post",))
    def favorite(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        is_in_favorite = recipe.in_favorites.filter(
            pk=current_user.pk
        ).exists()
        if is_in_favorite:
            raise validators.ValidationError(
                {"errors": "Рецепт уже есть в избранном."}
            )
        recipe.in_favorites.add(current_user)
        serializer = self.get_serializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        has_recipe_in_favorite = recipe.in_favorites.filter(
            pk=current_user.pk
        ).exists()
        if not has_recipe_in_favorite:
            raise validators.ValidationError(
                {"errors": "Этого рецепта нет в избранном."}
            )
        recipe.in_favorites.remove(current_user)
        return Response(status=status.HTTP_204_NO_CONTENT)
